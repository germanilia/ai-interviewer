"""
Judge prompt class for final interview response evaluation and refinement.
"""
import logging
import json
from sqlalchemy.orm import Session
from app.prompts.base_prompt import BasePrompt
from app.models.custom_prompt import PromptType
from app.schemas.interview_session import InterviewContext
from app.schemas.prompt_response import JudgeResponse, SmallLLMResponse
from app.core.llm_service import LLMFactory, ModelName, LLMResponse, LLMConfig, ReasoningConfig

logger = logging.getLogger(__name__)


class JudgePrompt(BasePrompt):
    """
    Judge prompt class for evaluating and refining interview responses.
    Uses a larger, more sophisticated model for final response generation.
    """

    DEFAULT_PROMPT = """You are a senior AI interviewer reviewing and refining interview responses.

Candidate Information:
- Name: {candidate_name}
- Position: {interview_title}
- Job Description: {job_description}

Interview Questions:
{questions}

Conversation History:
{conversation_history}

Current candidate message: "{current_message}"

Initial AI Response Analysis:
- Reasoning: {small_llm_reasoning}
- Proposed Response: {small_llm_response}
- Question Answered: {small_llm_was_question_answered}
- Question Index: {small_llm_answered_question_index}

Your task is to:
1. Review the initial AI response analysis
2. Evaluate if the analysis is accurate and appropriate
3. Refine or improve the response if needed
4. Provide your final judgment

Please respond in the following JSON format:
{{
    "reasoning": "Your reasoning for the final response and any refinements made",
    "response": "Your final refined response to the candidate",
    "was_question_answered": true/false,
    "answered_question_index": null or question number (1-based)
}}

Guidelines:
- Ensure responses are professional and engaging
- Verify question analysis accuracy
- Improve response quality if needed
- Maintain interview flow and momentum
- Consider cultural sensitivity and inclusivity
- Ensure responses encourage detailed candidate responses"""

    def __init__(self):
        # Use reasoning-enabled configuration for better analysis
        llm_config = LLMConfig(reasoning=ReasoningConfig(enabled=True, budget_tokens=1000))
        super().__init__(PromptType.JUDGE, self.DEFAULT_PROMPT)
        self.llm_client = LLMFactory.create_client(ModelName.CLAUDE_4_SONNET, config=llm_config)

    def execute(self, db: Session, context: InterviewContext, message: str, **kwargs) -> JudgeResponse:
        """
        Execute the judge prompt to evaluate and refine the interview response.

        Args:
            db: Database session
            context: Interview context
            message: Candidate's message
            **kwargs: Additional arguments including small_llm_response

        Returns:
            JudgeResponse with refined reasoning, response, and question analysis
        """
        try:
            # Get the small LLM response from kwargs
            small_llm_response = kwargs.get('small_llm_response')
            if not isinstance(small_llm_response, SmallLLMResponse):
                raise ValueError("small_llm_response is required and must be a SmallLLMResponse object")

            # Get the prompt content (custom or default)
            prompt_content = self.get_prompt_content(db)

            # Prepare context variables
            context_vars = self.prepare_context_variables(context, message)

            # Add small LLM response data to context variables
            context_vars.update({
                "small_llm_reasoning": small_llm_response.reasoning,
                "small_llm_response": small_llm_response.response,
                "small_llm_was_question_answered": small_llm_response.was_question_answered,
                "small_llm_answered_question_index": small_llm_response.answered_question_index or "null"
            })

            # Format the prompt
            formatted_prompt = self.format_prompt(prompt_content, **context_vars)

            # Execute the LLM
            logger.info("Executing Judge prompt")
            llm_response = self.llm_client.generate(formatted_prompt, LLMResponse)

            # Parse the JSON response
            try:
                response_data = json.loads(llm_response.text)

                # Validate required fields
                required_fields = ["reasoning", "response", "was_question_answered"]
                for field in required_fields:
                    if field not in response_data:
                        raise ValueError(f"Missing required field: {field}")

                # Create the response object
                judge_response = JudgeResponse(
                    reasoning=response_data["reasoning"],
                    response=response_data["response"],
                    was_question_answered=response_data["was_question_answered"],
                    answered_question_index=response_data.get("answered_question_index")
                )

                self.log_execution("Judge", True)
                return judge_response

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse Judge LLM response as JSON: {e}")
                # Fallback: use the small LLM response with judge reasoning
                return JudgeResponse(
                    reasoning=f"Judge failed to parse response, using small LLM output: {str(e)}",
                    response=small_llm_response.response,
                    was_question_answered=small_llm_response.was_question_answered,
                    answered_question_index=small_llm_response.answered_question_index
                )

        except Exception as e:
            error_msg = f"Failed to execute Judge prompt: {str(e)}"
            logger.exception(error_msg)
            self.log_execution("Judge", False, error_msg)

            # Fallback to small LLM response if available
            small_llm_response = kwargs.get('small_llm_response')
            if isinstance(small_llm_response, SmallLLMResponse):
                return JudgeResponse(
                    reasoning=f"Judge execution failed, using small LLM response: {error_msg}",
                    response=small_llm_response.response,
                    was_question_answered=small_llm_response.was_question_answered,
                    answered_question_index=small_llm_response.answered_question_index
                )
            else:
                # Ultimate fallback
                return JudgeResponse(
                    reasoning="Both Judge and Small LLM failed",
                    response="Thank you for your response. Could you tell me more about your experience?",
                    was_question_answered=False,
                    answered_question_index=None
                )


# Create instance for dependency injection
judge_prompt = JudgePrompt()