"""
Base evaluator class for handling custom prompts from database or default prompts.
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from app.models.custom_prompt import PromptType
from app.crud.custom_prompt import custom_prompt_dao
from app.schemas.interview_session import InterviewContext

logger = logging.getLogger(__name__)


class BaseEvaluator(ABC):
    """
    Abstract base class for all prompt types.
    Handles loading custom prompts from database or using default prompts.
    """

    def __init__(self, prompt_type: PromptType, default_prompt: str, init_prompt:str):
        """
        Initialize the base prompt.
        
        Args:
            prompt_type: The type of prompt (EVALUATION, JUDGE, GUARDRAILS)
            default_prompt: The default prompt content to use if no custom prompt is found
        """
        self.prompt_type = prompt_type
        self.init_prompt = init_prompt
        self.default_prompt = default_prompt
        self._cached_prompt: Optional[str] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl = 300  # Cache for 5 minutes

    def get_prompt_content(self, db: Session) -> str:
        """
        Get the prompt content, either from database (custom) or default.
        Uses caching to avoid frequent database queries.
        
        Args:
            db: Database session
            
        Returns:
            The prompt content to use
        """
        import time
        
        current_time = time.time()
        
        # Check if we have a valid cached prompt
        if (self._cached_prompt is not None and 
            self._cache_timestamp is not None and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._cached_prompt

        try:
            # Try to get custom prompt from database
            custom_prompt = custom_prompt_dao.get_active_by_type(db=db, prompt_type=self.prompt_type)
            
            if custom_prompt and custom_prompt.content:
                logger.info(f"Using custom prompt for {self.prompt_type}: {custom_prompt.name}")
                prompt_content = custom_prompt.content
            else:
                logger.info(f"Using default prompt for {self.prompt_type}")
                prompt_content = self.default_prompt
            prompt_content = self.init_prompt + prompt_content

            # Cache the result
            self._cached_prompt = prompt_content
            self._cache_timestamp = current_time
            
            return prompt_content
            
        except Exception as e:
            logger.warning(f"Failed to load custom prompt for {self.prompt_type}, using default: {e}")
            return self.init_prompt + self.default_prompt

    def clear_cache(self):
        """Clear the cached prompt content."""
        self._cached_prompt = None
        self._cache_timestamp = None

    def format_prompt(self, prompt_content: str, **kwargs) -> str:
        """
        Format the prompt content with provided variables.
        
        Args:
            prompt_content: The raw prompt content
            **kwargs: Variables to substitute in the prompt
            
        Returns:
            Formatted prompt content
        """
        try:
            return prompt_content.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing variable in prompt formatting: {e}")
            return prompt_content
        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            return prompt_content

    @abstractmethod
    def execute(self, db: Session, context: InterviewContext, message: str, **kwargs) -> Any:
        """
        Execute the prompt with the given context and message.
        This method must be implemented by subclasses.
        
        Args:
            db: Database session
            context: Interview context
            message: User message
            **kwargs: Additional arguments specific to the prompt type
            
        Returns:
            The result of executing the prompt (varies by prompt type)
        """
        pass

    def prepare_context_variables(self, context: InterviewContext, message: str) -> Dict[str, Any]:
        """
        Prepare common context variables for prompt formatting.
        
        Args:
            context: Interview context
            message: User message
            
        Returns:
            Dictionary of variables for prompt formatting
        """
        # Prepare questions text
        questions_text = ""
        if context.questions:
            questions_list = []
            for i, question in enumerate(context.questions, 1):
                questions_list.append(f"{i}. {question.question_text} - {question.importance} - {question.instructions}")
            questions_text = "\n".join(questions_list)

        # Prepare conversation history
        conversation_text = ""
        if context.conversation_history:
            conversation_list = []
            for msg in context.conversation_history:
                role = "Interviewer" if msg.role == "assistant" else "Candidate"
                conversation_list.append(f"{role}: {msg.content}")
            conversation_text = "\n".join(conversation_list)

        return {
            "candidate_name": context.candidate_name,
            "interview_title": context.interview_title,
            "job_description": context.job_description or "Not specified",
            "questions": questions_text,
            "conversation_history": conversation_text,
            "current_message": message,
            "total_questions": len(context.questions) if context.questions else 0,
            "conversation_length": len(context.conversation_history) if context.conversation_history else 0,
            "language": context.language
        }

    def log_execution(self, prompt_type: str, success: bool, error: Optional[str] = None):
        """
        Log the execution of the prompt.
        
        Args:
            prompt_type: Type of prompt executed
            success: Whether execution was successful
            error: Error message if execution failed
        """
        if success:
            logger.info(f"Successfully executed {prompt_type} prompt")
        else:
            logger.error(f"Failed to execute {prompt_type} prompt: {error}")


class PromptExecutionError(Exception):
    """Exception raised when prompt execution fails."""
    pass
