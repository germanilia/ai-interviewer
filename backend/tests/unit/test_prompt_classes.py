"""
Unit tests for prompt classes (EvaluationEvaluationPrompt, JudgeEvaluator, GuardrailsEvaluator).
"""
import pytest
from unittest.mock import Mock, patch
from backend.app.evaluators.initial_evaluator import InitialEvaluator
from backend.app.evaluators.judge_evaluator import JudgeEvaluator
from backend.app.evaluators.guardrails_evaluator import GuardrailsEvaluator
from app.schemas.interview_session import InterviewContext, ChatMessage
from app.schemas.prompt_response import EvaluationResponse, JudgeResponse
from app.schemas.question import QuestionResponse
from app.models.custom_prompt import PromptType
from app.models.interview import QuestionCategory, QuestionImportance
from app.crud.user import UserDAO
from app.crud.custom_prompt import CustomPromptDAO
from app.schemas.user import UserCreate
from app.schemas.custom_prompt import CustomPromptCreate
from datetime import datetime


@pytest.fixture
def test_user_id(db):
    """Create a test user and return its ID."""
    user_dao = UserDAO()
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    return created_user.id


@pytest.fixture
def sample_interview_context():
    """Create a sample interview context for testing."""
    questions = [
        QuestionResponse(
            id=1,
            title="Intro Question",
            instructions=None,
            question_text="Tell me about yourself",
            category=QuestionCategory.GENERAL,
            importance=QuestionImportance.MANDATORY,
            created_by_user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        QuestionResponse(
            id=2,
            title="Strengths Question",
            question_text="What are your strengths?",
            category=QuestionCategory.GENERAL,
            instructions=None,
            importance=QuestionImportance.ASK_ONCE,
            created_by_user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    
    conversation_history = [
        ChatMessage(
            role="assistant",
            content="Hello! Welcome to the interview.",
            timestamp=datetime.now()
        ),
        ChatMessage(
            role="user",
            content="Thank you, I'm excited to be here.",
            timestamp=datetime.now()
        )
    ]
    
    return InterviewContext(
        candidate_name="John Doe",
        interview_title="Software Engineer",
        job_description="We are looking for a skilled software engineer...",
        questions=questions,
        conversation_history=conversation_history
    )


class TestEvaluationPrompt:
    """Test cases for EvaluationPrompt class."""

    def test_evaluation_prompt_initialization(self):
        """Test EvaluationPrompt initialization."""
        prompt = InitialEvaluator()
        assert prompt.prompt_type == PromptType.EVALUATION
        assert prompt.default_prompt is not None
        assert "candidate_name" in prompt.default_prompt
        assert "interview_title" in prompt.default_prompt

    def test_get_prompt_content_uses_default_when_no_custom(self, db):
        """Test that get_prompt_content returns default when no custom prompt exists."""
        prompt = InitialEvaluator()
        content = prompt.get_prompt_content(db)
        assert content == prompt.default_prompt

    def test_get_prompt_content_uses_custom_when_available(self, db, test_user_id):
        """Test that get_prompt_content returns custom prompt when available."""
        # Create a custom prompt
        custom_prompt_dao = CustomPromptDAO()
        custom_prompt_create = CustomPromptCreate(
            prompt_type=PromptType.EVALUATION,
            name="Custom Evaluation Prompt",
            content="Custom prompt content for {candidate_name}",
            is_active=True,
            created_by_user_id=test_user_id
        )
        custom_prompt_dao.create(db, obj_in=custom_prompt_create, created_by_user_id=test_user_id)
        
        prompt = InitialEvaluator()
        content = prompt.get_prompt_content(db)
        assert content == "Custom prompt content for {candidate_name}"

    def test_prepare_context_variables(self, sample_interview_context):
        """Test prepare_context_variables method."""
        prompt = InitialEvaluator()
        variables = prompt.prepare_context_variables(sample_interview_context, "Test message")
        
        assert variables["candidate_name"] == "John Doe"
        assert variables["interview_title"] == "Software Engineer"
        assert variables["current_message"] == "Test message"
        assert variables["total_questions"] == 2
        assert variables["conversation_length"] == 2
        assert "Tell me about yourself" in variables["questions"]
        assert "Hello! Welcome to the interview." in variables["conversation_history"]

    @patch('app.prompts.evaluation_prompt.LLMFactory.create_client')
    def test_execute_success_with_valid_json(self, mock_llm_factory, db, sample_interview_context):
        """Test successful execution with valid JSON response."""
        # Mock LLM client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = '{"reasoning": "Test reasoning", "response": "Test response", "was_question_answered": true, "answered_question_index": 1}'
        mock_client.generate.return_value = mock_response
        mock_llm_factory.return_value = mock_client
        
        prompt = InitialEvaluator()
        result = prompt.execute(db, sample_interview_context, "Test message")
        
        assert isinstance(result, EvaluationResponse)
        assert result.reasoning == "Test reasoning"
        assert result.response == "Test response"
        assert result.was_question_answered is True
        assert result.answered_question_index == 1

    @patch('app.prompts.evaluation_prompt.LLMFactory.create_client')
    def test_execute_fallback_on_invalid_json(self, mock_llm_factory, db, sample_interview_context):
        """Test fallback behavior when LLM returns invalid JSON."""
        # Mock LLM client with invalid JSON
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        mock_client.generate.return_value = mock_response
        mock_llm_factory.return_value = mock_client
        
        prompt = InitialEvaluator()
        result = prompt.execute(db, sample_interview_context, "Test message")
        
        assert isinstance(result, EvaluationResponse)
        assert result.reasoning == "Failed to parse structured response from LLM"
        assert result.was_question_answered is False
        assert result.answered_question_index is None

    @patch('app.prompts.evaluation_prompt.LLMFactory.create_client')
    def test_execute_fallback_on_exception(self, mock_llm_factory, db, sample_interview_context):
        """Test fallback behavior when LLM execution raises exception."""
        # Mock LLM client to raise exception
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("LLM error")
        mock_llm_factory.return_value = mock_client
        
        prompt = InitialEvaluator()
        result = prompt.execute(db, sample_interview_context, "Test message")
        
        assert isinstance(result, EvaluationResponse)
        assert result.reasoning == "Error occurred during LLM processing"
        assert result.was_question_answered is False


class TestJudgeEvaluator:
    """Test cases for JudgeEvaluator class."""

    def test_judge_prompt_initialization(self):
        """Test JudgeEvaluator initialization."""
        prompt = JudgeEvaluator()
        assert prompt.prompt_type == PromptType.JUDGE
        assert prompt.default_prompt is not None
        assert "evaluation_reasoning" in prompt.default_prompt

    @patch('app.prompts.judge_prompt.LLMFactory.create_client')
    def test_execute_success(self, mock_llm_factory, db, sample_interview_context):
        """Test successful execution of judge prompt."""
        # Mock LLM client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = '{"reasoning": "Judge reasoning", "response": "Judge response", "was_question_answered": false, "answered_question_index": null}'
        mock_client.generate.return_value = mock_response
        mock_llm_factory.return_value = mock_client
        
        # Create evaluation response
        evaluation_response = EvaluationResponse(
            reasoning="Evaluation reasoning",
            response="Evaluation response",
            was_question_answered=True,
            answered_question_index=1,
            interview_complete=False
        )
        
        prompt = JudgeEvaluator()
        result = prompt.execute(db, sample_interview_context, "Test message", evaluation_response=evaluation_response)
        
        assert isinstance(result, JudgeResponse)
        assert result.reasoning == "Judge reasoning"
        assert result.response == "Judge response"
        assert result.was_question_answered is False
        assert result.answered_question_index is None

    def test_execute_missing_evaluation_response(self, db, sample_interview_context):
        """Test execution fails when evaluation_response is missing."""
        prompt = JudgeEvaluator()
        
        with pytest.raises(ValueError, match="evaluation_response is required"):
            prompt.execute(db, sample_interview_context, "Test message")

    @patch('app.prompts.judge_prompt.LLMFactory.create_client')
    def test_execute_fallback_to_evaluation_on_error(self, mock_llm_factory, db, sample_interview_context):
        """Test fallback to evaluation response when judge execution fails."""
        # Mock LLM client to raise exception
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("Judge error")
        mock_llm_factory.return_value = mock_client
        
        # Create evaluation LLM response
        evaluation_response = EvaluationResponse(
            reasoning="Evaluation reasoning",
            response="Evaluation response",
            was_question_answered=True,
            answered_question_index=1,
            interview_complete=False
        )
        
        prompt = JudgeEvaluator()
        result = prompt.execute(db, sample_interview_context, "Test message", evaluation_response=evaluation_response)
        
        assert isinstance(result, JudgeResponse)
        assert "Judge execution failed" in result.reasoning
        assert result.response == "Evaluation response"
        assert result.was_question_answered is True
        assert result.answered_question_index == 1


class TestGuardrailsEvaluator:
    """Test cases for GuardrailsEvaluator class."""

    def test_guardrails_prompt_initialization(self):
        """Test GuardrailsEvaluator initialization."""
        prompt = GuardrailsEvaluator()
        assert prompt.prompt_type == PromptType.GUARDRAILS
        assert prompt.default_prompt is not None
        assert "content safety" in prompt.default_prompt.lower()

    @patch('app.prompts.guardrails_prompt.LLMFactory.create_client')
    def test_execute_allows_continuation(self, mock_llm_factory, db, sample_interview_context):
        """Test execution when guardrails allow continuation."""
        # Mock LLM client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = '{"can_continue": true, "reason": null}'
        mock_client.generate.return_value = mock_response
        mock_llm_factory.return_value = mock_client
        
        prompt = GuardrailsEvaluator()
        result = prompt.execute(db, sample_interview_context, "This is appropriate content")
        
        assert result is True

    @patch('app.prompts.guardrails_prompt.LLMFactory.create_client')
    def test_execute_blocks_continuation(self, mock_llm_factory, db, sample_interview_context):
        """Test execution when guardrails block continuation."""
        # Mock LLM client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = '{"can_continue": false, "reason": "Inappropriate content detected"}'
        mock_client.generate.return_value = mock_response
        mock_llm_factory.return_value = mock_client
        
        prompt = GuardrailsEvaluator()
        result = prompt.execute(db, sample_interview_context, "Inappropriate content")
        
        assert result is False

    @patch('app.prompts.guardrails_prompt.LLMFactory.create_client')
    def test_execute_fallback_on_error(self, mock_llm_factory, db, sample_interview_context):
        """Test fallback behavior when guardrails execution fails."""
        # Mock LLM client to raise exception
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("Guardrails error")
        mock_llm_factory.return_value = mock_client
        
        prompt = GuardrailsEvaluator()
        result = prompt.execute(db, sample_interview_context, "Test message")
        
        # Should default to allowing continuation on error
        assert result is True

    @patch('app.prompts.guardrails_prompt.LLMFactory.create_client')
    def test_get_detailed_response(self, mock_llm_factory, db, sample_interview_context):
        """Test get_detailed_response method."""
        # Mock LLM client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = '{"can_continue": false, "reason": "Content flagged for review"}'
        mock_client.generate.return_value = mock_response
        mock_llm_factory.return_value = mock_client
        
        prompt = GuardrailsEvaluator()
        result = prompt.get_detailed_response(db, sample_interview_context, "Flagged content")
        
        assert result.can_continue is False
        assert result.reason == "Content flagged for review"


class TestBasePromptFunctionality:
    """Test cases for base prompt functionality."""

    def test_format_prompt_with_variables(self):
        """Test format_prompt method with valid variables."""
        prompt = InitialEvaluator()
        template = "Hello {name}, welcome to {company}"
        result = prompt.format_prompt(template, name="John", company="TechCorp")
        assert result == "Hello John, welcome to TechCorp"

    def test_format_prompt_missing_variables(self):
        """Test format_prompt method with missing variables."""
        prompt = InitialEvaluator()
        template = "Hello {name}, welcome to {company}"
        result = prompt.format_prompt(template, name="John")  # Missing company
        # Should return original template when variables are missing
        assert result == template

    def test_clear_cache(self, db):
        """Test clear_cache method."""
        prompt = InitialEvaluator()
        
        # Get content to populate cache
        prompt.get_prompt_content(db)
        assert prompt._cached_prompt is not None
        
        # Clear cache
        prompt.clear_cache()
        assert prompt._cached_prompt is None
        assert prompt._cache_timestamp is None
