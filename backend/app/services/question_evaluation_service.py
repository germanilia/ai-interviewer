"""
Question evaluation service for determining if interview questions were answered.
"""
import logging
from typing import TYPE_CHECKING
from sqlalchemy.orm import Session

from app.evaluators.base_evaluator import BaseEvaluator
from app.models.custom_prompt import PromptType
from app.schemas.prompt_response import QuestionEvaluationResponse
from app.schemas.interview_session import InterviewContext, ChatMessage
from app.core.llm_service import LLMFactory, ModelName

if TYPE_CHECKING:
    from app.schemas.question import QuestionResponse

logger = logging.getLogger(__name__)


class QuestionEvaluationService(BaseEvaluator):
    """Service for evaluating if interview questions were answered using Claude 4"""

    INIT_PROMPT = """
You are an expert interview evaluator. Your task is to determine if a specific interview question has been fully answered by the candidate based on the conversation history.

Interview Context:
- Candidate: {candidate_name}
- Position: {interview_title}
- Job Description: {job_description}

Current Question Being Evaluated:
{current_question}

Full Conversation History:
{conversation_history}
"""

    DEFAULT_PROMPT = """
Your task:
1. Analyze the conversation history to determine if the candidate has provided a complete and satisfactory answer to the current question
2. Consider the depth, relevance, and completeness of the candidate's response
3. A question is "fully answered" if the candidate has addressed the core aspects of what was being asked
4. Partial answers, evasive responses, or off-topic responses should be considered as NOT fully answered

Please provide your evaluation in the following format:
- reasoning: Your detailed analysis of why the question was or wasn't fully answered
- question_fully_answered: true if the question was completely answered, false otherwise

Be strict in your evaluation - only mark as fully answered if the candidate genuinely addressed the question comprehensively.
"""

    def __init__(self):
        """Initialize the question evaluation service with Claude 4"""
        super().__init__(PromptType.QUESTION_EVALUATION, self.DEFAULT_PROMPT, self.INIT_PROMPT)
        self.llm_client = LLMFactory.create_client(ModelName.CLAUDE_4_SONNET)

    def execute(self, db: Session, context: InterviewContext, message: str, **kwargs) -> bool:
        """
        Execute the question evaluation prompt (required by BaseEvaluator).

        Args:
            db: Database session
            context: Interview context
            message: User message
            **kwargs: Additional arguments (should include 'current_question')

        Returns:
            Boolean indicating if question was fully answered
        """
        current_question = kwargs.get('current_question')
        if not current_question:
            logger.error("current_question not provided in kwargs")
            return False

        response = self.evaluate_question_answered(db, context, current_question, message)
        return response.question_fully_answered

    def evaluate_question_answered(
        self,
        db: Session,
        context: InterviewContext,
        current_question: "QuestionResponse",
        user_message: str
    ) -> QuestionEvaluationResponse:
        """
        Evaluate if the current question was fully answered based on conversation history.

        Args:
            db: Database session
            context: Interview context with conversation history
            current_question: The question being evaluated
            user_message: The latest user message

        Returns:
            QuestionEvaluationResponse with evaluation results
        """
        logger.info(f"Evaluating if question '{current_question.title}' was answered")

        try:
            # Get the prompt content (custom or default)
            prompt_content = self.get_prompt_content(db)

            # Format the current question
            question_text = f"Title: {current_question.title}\nQuestion: {current_question.question_text}"
            if current_question.instructions:
                question_text += f"\nInstructions: {current_question.instructions}"

            # Prepare context variables
            context_vars = self.prepare_context_variables(context, user_message)
            context_vars['current_question'] = question_text

            # Format the prompt
            formatted_prompt = self.format_prompt(prompt_content, **context_vars)

            # Execute the LLM evaluation
            logger.info("Executing question evaluation with Claude 4")
            evaluation_response = self.llm_client.generate(formatted_prompt, QuestionEvaluationResponse)
            logger.info(f"Question evaluation completed: {evaluation_response.question_fully_answered}")

            self.log_execution("Question Evaluation", True)
            return evaluation_response

        except Exception as e:
            logger.exception(f"Error in question evaluation: {e}")
            self.log_execution("Question Evaluation", False, str(e))
            # Fallback to not answered to be safe
            return QuestionEvaluationResponse(
                reasoning=f"Evaluation failed due to error: {str(e)}. Defaulting to not answered.",
                question_fully_answered=False
            )

    def _format_conversation_history(self, conversation_history: list[ChatMessage]) -> str:
        """Format conversation history for the prompt"""
        if not conversation_history:
            return "No conversation history available."

        formatted_messages = []
        for msg in conversation_history:
            role = "Interviewer" if msg.role == "assistant" else "Candidate"
            formatted_messages.append(f"{role}: {msg.content}")

        return "\n".join(formatted_messages)


# Service instance for dependency injection
question_evaluation_service = QuestionEvaluationService()
