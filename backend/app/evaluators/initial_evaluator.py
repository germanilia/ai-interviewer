"""
Evaluation prompt class for initial interview response generation.
"""
import logging
import json
from typing import Optional
from sqlalchemy.orm import Session
from app.evaluators.base_evaluator import BaseEvaluator, PromptExecutionError
from app.models.custom_prompt import PromptType
from app.schemas.interview_session import InterviewContext
from app.schemas.prompt_response import EvaluationResponse
from app.core.llm_service import LLMFactory, ModelName, LLMResponse

logger = logging.getLogger(__name__)


class InitialEvaluator(BaseEvaluator):
    """
    Evaluation prompt class for generating initial interview responses.
    Uses a smaller, faster model for quick response generation.
    """

    INIT_PROMPT = """
You are an AI interviewer conducting a professional interview for the position of {interview_title}.

Candidate Information:
- Name: {candidate_name}
- Position: {interview_title}
- Job Description: {job_description}

Interview Questions:
{questions}

Conversation History:
{conversation_history}

Current candidate message: "{current_message}"

You are required to respond in the following language: "{language}"
"""

    DEFAULT_PROMPT = """

Your task is to:
1. Analyze the candidate's response
2. Determine if they answered a specific question from the list
3. Generate an appropriate follow-up response
4. You need to pay attention to the questions by the following rules:
   - If the question is marked as "mandatory", you must ask it until you are satisfied with the answer and it's a complete one.
   - If the question is marked as "ask_once", you should ask it only once, and you will accept any answer.
   - If the question is marked as "optional", you will ask it once, if the candidate chose not to answer you will continue.
5. You need to pay attention to the instructions for each question and make sure you are not missing any important points.
6. Once a question was answered according to the rules provided, you will proceed to the next question on the questions list.
7. If you finished asking all the questions, you will end the interview. Mark interview_complete as False if the interview is still ongoing otherwise mark it as True.

Guidelines:
- Be professional and engaging
- Ask follow-up questions to dive deeper
- If a question was answered, note which one
- Keep responses conversational but focused
- Encourage detailed responses from the candidate
"""


    def __init__(self):
        super().__init__(PromptType.EVALUATION, self.DEFAULT_PROMPT, self.INIT_PROMPT)
        self.llm_client = LLMFactory.create_client(ModelName.CLAUDE_3_5_HAIKU)

    def execute(self, db: Session, context: InterviewContext, message: str, **kwargs) -> EvaluationResponse:
        """
        Execute the evaluation prompt to generate an interview response.

        Args:
            db: Database session
            context: Interview context
            message: Candidate's message
            **kwargs: Additional arguments (e.g., language preference)

        Returns:
            EvaluationResponse with reasoning, response, and question analysis
        """
        
        # Get the prompt content (custom or default)
        prompt_content = self.get_prompt_content(db)

        # Prepare context variables
        context_vars = self.prepare_context_variables(context, message)

        # Format the prompt
        formatted_prompt = self.format_prompt(prompt_content, **context_vars)

        # Execute the LLM
        logger.info("Executing Evaluation prompt")
        evaluation_response = self.llm_client.generate(formatted_prompt, EvaluationResponse)
        self.log_execution("Evaluation", True)
        return evaluation_response
# Create instance for dependency injection
evaluation_prompt = InitialEvaluator()