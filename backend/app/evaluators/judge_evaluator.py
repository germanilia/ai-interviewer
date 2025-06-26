"""
Judge prompt class for final interview response evaluation and refinement.
"""
import logging
import json
from sqlalchemy.orm import Session
from app.evaluators.base_evaluator import BaseEvaluator
from app.models.custom_prompt import PromptType
from app.schemas.interview_session import InterviewContext
from app.schemas.prompt_response import JudgeResponse, EvaluationResponse
from app.core.llm_service import LLMFactory, ModelName, LLMConfig, ReasoningConfig

logger = logging.getLogger(__name__)


class JudgeEvaluator(BaseEvaluator):
    """
    Judge prompt class for evaluating and refining interview responses.
    Uses a larger, more sophisticated model for final response generation.
    """
    INIT_PROMPT = """
You are a senior AI interviewer reviewing and refining interview responses.

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
- Reasoning: {evaluation_reasoning}
- Proposed Response: {evaluation_response}
- Question Answered: {evaluation_was_question_answered}
- Question Index: {evaluation_answered_question_index}

"""
    DEFAULT_PROMPT = """
Your task is to:
1. Review the initial AI response analysis
2. Evaluate if the analysis is accurate and appropriate
3. Refine or improve the response if needed
4. Provide your final judgment

Guidelines:
- Ensure responses are professional and engaging
- Verify question analysis accuracy
- Improve response quality if needed
- Maintain interview flow and momentum
- Consider cultural sensitivity and inclusivity
- Ensure responses encourage detailed candidate responses"""

    def __init__(self):
        # Use reasoning-enabled configuration for better analysis
        llm_config = LLMConfig(reasoning=ReasoningConfig(
            enabled=True, budget_tokens=1000))
        super().__init__(PromptType.JUDGE, self.DEFAULT_PROMPT, self.INIT_PROMPT)
        self.llm_client = LLMFactory.create_client(
            ModelName.CLAUDE_4_SONNET, config=llm_config)

    def execute(self, db: Session, context: InterviewContext, message: str, **kwargs) -> JudgeResponse:
        """
        Execute the judge prompt to evaluate and refine the interview response.

        Args:
            db: Database session
            context: Interview context
            message: Candidate's message
            **kwargs: Additional arguments including evaluation_response

        Returns:
            JudgeResponse with refined reasoning, response, and question analysis
        """
        try:
            # Get the evaluation response from kwargs
            evaluation_response = kwargs.get('evaluation_response')
            if not isinstance(evaluation_response, EvaluationResponse):
                raise ValueError(
                    "evaluation_response is required and must be a EvaluationResponse object")

            # Get the prompt content (custom or default)
            prompt_content = self.get_prompt_content(db)

            # Prepare context variables
            context_vars = self.prepare_context_variables(context, message)

            # Add evaluation response data to context variables
            context_vars.update({
                "evaluation_reasoning": evaluation_response.reasoning,
                "evaluation_response": evaluation_response.response,
                "evaluation_was_question_answered": evaluation_response.was_question_answered,
                "evaluation_answered_question_index": evaluation_response.answered_question_index or "null"
            })

            # Format the prompt
            formatted_prompt = self.format_prompt(
                prompt_content, **context_vars)

            # Execute the LLM
            logger.info("Executing Judge prompt")
            llm_response = self.llm_client.generate(
                formatted_prompt, JudgeResponse)

            # Parse the JSON response
            try:
                judge_response = json.loads(llm_response.text)
                self.log_execution("Judge", True)
                return judge_response

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"Failed to parse Judge LLM response as JSON: {e}")
                # Fallback: use the evaluation response with judge reasoning
                return JudgeResponse(
                    reasoning=f"Judge failed to parse response, using evaluation output: {str(e)}",
                    response=evaluation_response.response,
                    was_question_answered=evaluation_response.was_question_answered,
                    answered_question_index=evaluation_response.answered_question_index
                )

        except Exception as e:
            error_msg = f"Failed to execute Judge prompt: {str(e)}"
            logger.exception(error_msg)
            self.log_execution("Judge", False, error_msg)

            # Fallback to evaluation response if available
            evaluation_response = kwargs.get('evaluation_response')
            if isinstance(evaluation_response, EvaluationResponse):
                return JudgeResponse(
                    reasoning=f"Judge execution failed, using evaluation response: {error_msg}",
                    response=evaluation_response.response,
                    was_question_answered=evaluation_response.was_question_answered,
                    answered_question_index=evaluation_response.answered_question_index
                )
            else:
                # Ultimate fallback
                return JudgeResponse(
                    reasoning="Both Judge and Evaluation failed",
                    response="Thank you for your response. Could you tell me more about your experience?",
                    was_question_answered=False,
                    answered_question_index=None
                )


# Create instance for dependency injection
judge_prompt = JudgeEvaluator()
