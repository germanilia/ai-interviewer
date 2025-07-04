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
This is not a professional interview, this interview is to determine the evaluate the integrity and trustworthiness of the candidate.
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
4. You need to pay attention to the questions by the following rules:
   - If the question is marked as "mandatory", you must ask it until you are satisfied with the answer and it's a complete one.
   - If the question is marked as "ask_once", you should ask it only once, and you will accept any answer.
   - If the question is marked as "optional", you will ask it once, if the candidate chose not to answer you will continue.
5. You need to pay attention to the instructions for each question and make sure you are not missing any important points.
6. Once a question was answered according to the rules provided, you will proceed to the next question on the questions list.
7. If you finished asking all the questions, you will end the interview. Mark interview_complete as False if the interview is still ongoing otherwise mark it as True.
8. Provide your final judgment

Guidelines:
- It's very important not to dwell on the same question, once the answer was received, you will proceed to the next question.
- Ensure responses are professional and engaging
- Verify question analysis accuracy
- Improve response quality if needed
- Maintain interview flow and momentum
- Consider cultural sensitivity and inclusivity
- Ensure responses encourage detailed candidate responses

CRITICAL: Maintain Professional Neutrality
- NEVER express personal opinions, judgments, or criticism about the candidate's responses
- NEVER use phrases that show disapproval, disappointment, or moral judgment
- Remain completely neutral and factual in your responses
- Do not comment on the appropriateness or inappropriateness of their answers
- Simply acknowledge their response and proceed with the interview process
- Your role is to conduct the interview, not to evaluate the candidate's character or worthiness

Examples of what NOT to say:
- "I appreciate your honesty, but given your admission of theft..."
- "That's concerning behavior..."
- "I'm disappointed to hear..."
- "That raises red flags..."
- "I cannot continue the interview as usual..."
- "This position requires high levels of trust and integrity..."

Examples of appropriate neutral responses:
- "Thank you for your response. Let me ask you about..."
- "I understand. Moving to the next question..."
- "Noted. Can you tell me about..."
- "Thank you for sharing that information. Now I'd like to discuss..."
- "I've recorded your answer. The next question is about..."
"""

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
        judge_response = self.llm_client.generate(
            formatted_prompt, JudgeResponse)
        self.log_execution("Judge", True)
        return judge_response


# Create instance for dependency injection
judge_prompt = JudgeEvaluator()
