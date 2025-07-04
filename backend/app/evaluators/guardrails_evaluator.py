"""
Guardrails prompt class for content safety and appropriateness checking.
"""
import logging
import json
from sqlalchemy.orm import Session
from app.evaluators.base_evaluator import BaseEvaluator
from app.models.custom_prompt import PromptType
from app.schemas.interview_session import InterviewContext
from app.schemas.prompt_response import GuardrailsResponse
from app.core.llm_service import LLMFactory, ModelName, LLMResponse

logger = logging.getLogger(__name__)


class GuardrailsEvaluator(BaseEvaluator):
    """
    Guardrails evaluator for checking if conversation stays within interview context.
    Only blocks system misuse, spam, or conversations that have completely abandoned the interview context.
    Does NOT evaluate job fitness, character, or appropriateness of interview responses.
    """
    INIT_PROMPT = """
You are a conversation context monitor for professional interviews. Your role is to ensure the conversation stays within the interview context and is not being misused for other purposes.

Interview Context:
- Position: {interview_title}
- Candidate: {candidate_name}
- Job Description: {job_description}

Conversation History:
{conversation_history}

Current candidate message: "{current_message}"
"""

    DEFAULT_PROMPT = """

Your ONLY task is to determine if the conversation is staying within the interview context or if it has been diverted to unrelated topics.

You should ONLY flag conversations that:
1. Are attempting to use the system for purposes other than the interview (e.g., asking for help with homework, general chatting, technical support)
2. Contain spam or automated/bot-like behavior
3. Are trying to manipulate the system to perform non-interview tasks
4. Have completely abandoned the interview context and moved to unrelated discussions

You should ALWAYS ALLOW conversations that:
- Discuss any work-related experiences, regardless of content (including admissions of misconduct, mistakes, illegal activities, etc.)
- Answer interview questions honestly, even with controversial or negative content
- Stay within the professional interview context, even if discussing sensitive topics
- Include personal anecdotes related to work experience or character assessment
- Contain any content that could reasonably be part of an integrity/trustworthiness interview

CRITICAL GUIDELINES:
- You are NOT evaluating job fitness, character, or qualifications
- You are NOT making moral or ethical judgments about the candidate's responses
- You are ONLY checking if this is still an interview conversation vs. system misuse
- Ethical issues, admissions of wrongdoing, controversial opinions are ALL ALLOWED as long as they're interview-related
- Be extremely permissive - only block obvious system misuse or spam

Examples of what to BLOCK:
- "Can you help me write my resume?"
- "What's the weather like today?"
- "Please translate this text for me"
- "How do I fix my computer?"
- Obvious spam or gibberish

Examples of what to ALLOW:
- Any admission of past misconduct (theft, lying, cheating, etc.)
- Controversial political or social opinions
- Negative experiences with previous employers
- Personal struggles or challenges
- Any response to interview questions, regardless of content

"""

    def __init__(self):
        super().__init__(PromptType.GUARDRAILS, self.DEFAULT_PROMPT, self.INIT_PROMPT)
        self.llm_client = LLMFactory.create_client(ModelName.CLAUDE_3_5_HAIKU)

    def execute(self, db: Session, context: InterviewContext, message: str, **kwargs) -> bool:
        """
        Execute the guardrails prompt to check if conversation can continue.

        Args:
            db: Database session
            context: Interview context
            message: Candidate's message
            **kwargs: Additional arguments

        Returns:
            Boolean indicating whether conversation can continue
        """
        try:
            # Get the prompt content (custom or default)
            prompt_content = self.get_prompt_content(db)

            # Prepare context variables
            context_vars = self.prepare_context_variables(context, message)

            # Format the prompt
            formatted_prompt = self.format_prompt(
                prompt_content, **context_vars)

            # Execute the LLM
            logger.info("Executing Guardrails prompt")
            llm_response = self.llm_client.generate(
                formatted_prompt, GuardrailsResponse)

            try:
                can_continue = llm_response.can_continue
                reason = llm_response.reason

                if not can_continue and reason:
                    logger.warning(
                        f"Guardrails blocked conversation: {reason}")
                else:
                    logger.info(
                        "Guardrails approved conversation continuation")

                self.log_execution("Guardrails", True)
                return can_continue

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"Failed to parse Guardrails LLM response as JSON: {e}")
                # Fallback: allow conversation to continue if we can't parse the response
                logger.info(
                    "Guardrails defaulting to allow due to parsing error")
                return True

        except Exception as e:
            error_msg = f"Failed to execute Guardrails prompt: {str(e)}"
            logger.exception(error_msg)
            self.log_execution("Guardrails", False, error_msg)

            # Fallback: allow conversation to continue if guardrails fail
            logger.info(
                "Guardrails defaulting to allow due to execution error")
            return True

    def get_detailed_response(self, db: Session, context: InterviewContext, message: str, **kwargs) -> GuardrailsResponse:
        """
        Execute the guardrails prompt and return detailed response with reasoning.

        Args:
            db: Database session
            context: Interview context
            message: Candidate's message
            **kwargs: Additional arguments

        Returns:
            GuardrailsResponse with detailed information
        """
        try:
            # Get the prompt content (custom or default)
            prompt_content = self.get_prompt_content(db)

            # Prepare context variables
            context_vars = self.prepare_context_variables(context, message)

            # Format the prompt
            formatted_prompt = self.format_prompt(
                prompt_content, **context_vars)

            # Execute the LLM
            logger.info("Executing Guardrails prompt (detailed)")
            llm_response = self.llm_client.generate(
                formatted_prompt, LLMResponse)

            # Parse the JSON response
            try:
                response_data = json.loads(llm_response.text)

                # Validate required fields
                if "can_continue" not in response_data:
                    raise ValueError("Missing required field: can_continue")

                guardrails_response = GuardrailsResponse(
                    can_continue=response_data["can_continue"],
                    reason=response_data.get("reason")
                )

                self.log_execution("Guardrails (detailed)", True)
                return guardrails_response

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"Failed to parse Guardrails LLM response as JSON: {e}")
                # Fallback: allow conversation to continue
                return GuardrailsResponse(
                    can_continue=True,
                    reason=f"Parsing error: {str(e)}"
                )

        except Exception as e:
            error_msg = f"Failed to execute Guardrails prompt: {str(e)}"
            logger.exception(error_msg)
            self.log_execution("Guardrails (detailed)", False, error_msg)

            # Fallback: allow conversation to continue
            return GuardrailsResponse(
                can_continue=True,
                reason=f"Execution error: {error_msg}"
            )


# Create instance for dependency injection
guardrails_prompt = GuardrailsEvaluator()
