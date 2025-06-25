"""
Small LLM prompt class for initial interview response generation.
"""
import logging
import json
from typing import Optional
from sqlalchemy.orm import Session
from app.prompts.base_prompt import BasePrompt, PromptExecutionError
from app.models.custom_prompt import PromptType
from app.schemas.interview_session import InterviewContext
from app.schemas.prompt_response import SmallLLMResponse
from app.core.llm_service import LLMFactory, ModelName, LLMResponse

logger = logging.getLogger(__name__)


class SmallLLMPrompt(BasePrompt):
    """
    Small LLM prompt class for generating initial interview responses.
    Uses a smaller, faster model for quick response generation.
    """

    DEFAULT_PROMPT = """You are an AI interviewer conducting a professional interview for the position of {interview_title}.

Candidate Information:
- Name: {candidate_name}
- Position: {interview_title}
- Job Description: {job_description}

Interview Questions:
{questions}

Conversation History:
{conversation_history}

Current candidate message: "{current_message}"

Your task is to:
1. Analyze the candidate's response
2. Determine if they answered a specific question from the list
3. Generate an appropriate follow-up response

Please respond in the following JSON format:
{{
    "reasoning": "Your reasoning for the response and analysis",
    "response": "Your response to the candidate",
    "was_question_answered": true/false,
    "answered_question_index": null or question number (1-based)
}}

Guidelines:
- Be professional and engaging
- Ask follow-up questions to dive deeper
- If a question was answered, note which one
- Keep responses conversational but focused
- Encourage detailed responses from the candidate"""

    def __init__(self):
        super().__init__(PromptType.SMALL_LLM, self.DEFAULT_PROMPT)
        self.llm_client = LLMFactory.create_client(ModelName.CLAUDE_3_5_HAIKU)

    def execute(self, db: Session, context: InterviewContext, message: str, **kwargs) -> SmallLLMResponse:
        """
        Execute the small LLM prompt to generate an interview response.

        Args:
            db: Database session
            context: Interview context
            message: Candidate's message
            **kwargs: Additional arguments (e.g., language preference)

        Returns:
            SmallLLMResponse with reasoning, response, and question analysis
        """
        try:
            # Get the prompt content (custom or default)
            prompt_content = self.get_prompt_content(db)

            # Prepare context variables
            context_vars = self.prepare_context_variables(context, message)

            # Format the prompt
            formatted_prompt = self.format_prompt(prompt_content, **context_vars)

            # Execute the LLM
            logger.info("Executing Small LLM prompt")
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
                small_llm_response = SmallLLMResponse(
                    reasoning=response_data["reasoning"],
                    response=response_data["response"],
                    was_question_answered=response_data["was_question_answered"],
                    answered_question_index=response_data.get("answered_question_index")
                )

                self.log_execution("SmallLLM", True)
                return small_llm_response

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse LLM response as JSON: {e}")
                # Fallback: create a basic response
                return SmallLLMResponse(
                    reasoning="Failed to parse structured response from LLM",
                    response=llm_response.text[:500] if llm_response.text else "I understand. Could you tell me more about that?",
                    was_question_answered=False,
                    answered_question_index=None
                )

        except Exception as e:
            error_msg = f"Failed to execute Small LLM prompt: {str(e)}"
            logger.exception(error_msg)
            self.log_execution("SmallLLM", False, error_msg)

            # Return a fallback response
            return SmallLLMResponse(
                reasoning="Error occurred during LLM processing",
                response="Thank you for your response. Could you elaborate on that point?",
                was_question_answered=False,
                answered_question_index=None
            )


# Create instance for dependency injection
small_llm_prompt = SmallLLMPrompt()