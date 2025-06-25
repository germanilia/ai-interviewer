"""
Unit tests for InterviewQuestionDAO to verify proper database operations and Pydantic object returns.
"""
import pytest
from datetime import datetime, timezone
from app.schemas.interview_question import InterviewQuestionCreate, InterviewQuestionUpdate, InterviewQuestionResponse
from app.schemas.interview import InterviewCreate
from app.schemas.question import QuestionCreate
from app.schemas.user import UserCreate
from app.models.interview import InterviewQuestionStatus, QuestionImportance, QuestionCategory
from app.crud.user import UserDAO
from app.crud.question import QuestionDAO
from app.crud.interview import InterviewDAO
from app.crud.interview_question import InterviewQuestionDAO


@pytest.fixture
def test_user(db):
    """Create a test user and return it."""
    user_dao = UserDAO()
    user_create = UserCreate(
        username="testuser_iq",
        email="test_iq@example.com",
        full_name="Test User IQ"
    )
    return user_dao.create(db, obj_in=user_create)


@pytest.fixture
def test_question(db, test_user):
    """Helper function to create a test question and return it."""
    question_dao = QuestionDAO()
    question_create = QuestionCreate(
        title="Test Question",
        question_text="This is a test question with sufficient length for validation.",
        instructions="Test instructions for this question",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.GENERAL,
        created_by_user_id=test_user.id
    )
    return question_dao.create(db, obj_in=question_create)


@pytest.fixture
def test_interview(db, test_user, test_question):
    """Fixture to create a test interview."""
    interview_dao = InterviewDAO()
    interview_create = InterviewCreate(
        job_title="Software Engineer",
        job_description="Test job description",
        question_ids=[test_question.id]
    )
    return interview_dao.create(db, obj_in=interview_create, created_by_user_id=test_user.id)


@pytest.fixture
def interview_question_dao():
    """Fixture to provide an instance of InterviewQuestionDAO."""
    return InterviewQuestionDAO()


def test_interview_question_dao_create_returns_pydantic_object(db, interview_question_dao, test_interview, test_question):
    """Test that InterviewQuestionDAO.create returns an InterviewQuestionResponse (Pydantic object)."""
    interview_question_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=test_question.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot=test_question.question_text
    )
    
    result = interview_question_dao.create(db, obj_in=interview_question_create)
    
    assert isinstance(result, InterviewQuestionResponse)
    assert result.interview_id == test_interview.id
    assert result.question_id == test_question.id
    assert result.status == InterviewQuestionStatus.PENDING
    assert result.order_index == 1
    assert result.question_text_snapshot == test_question.question_text
    assert result.id is not None
    assert result.candidate_answer is None
    assert result.ai_analysis is None


def test_interview_question_dao_get_returns_pydantic_object(db, interview_question_dao, test_interview, test_question):
    """Test that InterviewQuestionDAO.get returns an InterviewQuestionResponse (Pydantic object)."""
    interview_question_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=test_question.id,
        status=InterviewQuestionStatus.ASKED,
        order_index=2,
        question_text_snapshot=test_question.question_text
    )
    created_interview_question = interview_question_dao.create(db, obj_in=interview_question_create)
    
    result = interview_question_dao.get(db, created_interview_question.id)
    
    assert isinstance(result, InterviewQuestionResponse)
    assert result.interview_id == test_interview.id
    assert result.question_id == test_question.id
    assert result.status == InterviewQuestionStatus.ASKED
    assert result.order_index == 2
    assert result.id == created_interview_question.id


def test_interview_question_dao_get_nonexistent_returns_none(db, interview_question_dao):
    """Test that getting a non-existent interview question returns None."""
    result = interview_question_dao.get(db, 99999)
    assert result is None


def test_interview_question_dao_get_multi_returns_pydantic_objects(db, interview_question_dao, test_user, test_interview):
    """Test that InterviewQuestionDAO.get_multi returns a list of InterviewQuestionResponse objects."""
    question_dao = QuestionDAO()
    for i in range(3):
        question_create = QuestionCreate(
            title=f"Question {i}",
            question_text=f"This is a detailed question text for question number {i} with sufficient length",
            instructions=f"Test instructions for question {i}",
            importance=QuestionImportance.ASK_ONCE,
            category=QuestionCategory.ETHICS,
            created_by_user_id=test_user.id
        )
        created_question = question_dao.create(db, obj_in=question_create)
        interview_question_create = InterviewQuestionCreate(
            interview_id=test_interview.id,
            question_id=created_question.id,
            status=InterviewQuestionStatus.PENDING,
            order_index=i + 1,
            question_text_snapshot=created_question.question_text
        )
        interview_question_dao.create(db, obj_in=interview_question_create)

    results = interview_question_dao.get_multi(db)
    assert isinstance(results, list)
    # This will fail if other tests created interview_questions, so we check for at least 3
    assert len(results) >= 3 
    assert all(isinstance(item, InterviewQuestionResponse) for item in results)


def test_interview_question_dao_update_returns_pydantic_object(db, interview_question_dao, test_interview, test_question):
    """Test that InterviewQuestionDAO.update returns an InterviewQuestionResponse (Pydantic object)."""
    interview_question_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=test_question.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot=test_question.question_text
    )
    created_interview_question = interview_question_dao.create(db, obj_in=interview_question_create)
    
    db_obj = interview_question_dao.get_db_obj(db, id=created_interview_question.id)

    update_schema = InterviewQuestionUpdate(
        status=InterviewQuestionStatus.ANSWERED,
        candidate_answer="This is the candidate's answer."
    )
    
    result = interview_question_dao.update(db, db_obj=db_obj, obj_in=update_schema)
    
    assert isinstance(result, InterviewQuestionResponse)
    assert result.id == created_interview_question.id
    assert result.status == InterviewQuestionStatus.ANSWERED
    assert result.candidate_answer == "This is the candidate's answer."
    assert result.order_index == 1 # Should not change


def test_interview_question_dao_delete_returns_true(db, interview_question_dao, test_interview, test_question):
    """Test that InterviewQuestionDAO.delete returns True for a successful deletion."""
    interview_question_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=test_question.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot=test_question.question_text
    )
    created_interview_question = interview_question_dao.create(db, obj_in=interview_question_create)
    
    result = interview_question_dao.delete(db, id=created_interview_question.id)
    
    assert result is True
    assert interview_question_dao.get(db, created_interview_question.id) is None


def test_interview_question_dao_delete_nonexistent_returns_false(db, interview_question_dao):
    """Test that deleting a non-existent interview question returns False."""
    result = interview_question_dao.delete(db, id=99999)
    assert result is False


def test_get_by_interview_returns_correctly_ordered_questions(db, interview_question_dao, test_user, test_interview):
    """Test that get_by_interview returns questions for a specific interview, ordered by order_index."""
    question_dao = QuestionDAO()
    questions_data = []
    for i in range(3):
        question_create = QuestionCreate(
            title=f"Ordered Question {i}",
            question_text=f"Ordered question text {i}",
            instructions=f"Test instructions for ordered question {i}",
            importance=QuestionImportance.MANDATORY,
            category=QuestionCategory.GENERAL,
            created_by_user_id=test_user.id
        )
        created_question = question_dao.create(db, obj_in=question_create)
        questions_data.append(created_question)

    # Create in reverse order to test ordering
    for i, question in reversed(list(enumerate(questions_data))):
        interview_question_create = InterviewQuestionCreate(
            interview_id=test_interview.id,
            question_id=question.id,
            status=InterviewQuestionStatus.PENDING,
            order_index=i,
            question_text_snapshot=question.question_text
        )
        interview_question_dao.create(db, obj_in=interview_question_create)

    results = interview_question_dao.get_by_interview(db, interview_id=test_interview.id)
    
    assert len(results) >= 3 # At least 3 were added
    assert all(isinstance(r, InterviewQuestionResponse) for r in results)
    assert all(r.interview_id == test_interview.id for r in results)
    
    # Check order
    order_indices = [r.order_index for r in results]
    assert order_indices == sorted(order_indices)


def test_get_by_status_returns_correct_questions(db, interview_question_dao, test_interview, test_question):
    """Test that get_by_status returns questions filtered by their status."""
    # Create one pending and one asked question
    iq_pending_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=test_question.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot=test_question.question_text
    )
    interview_question_dao.create(db, obj_in=iq_pending_create)

    # Need another question for the second interview_question
    question_dao = QuestionDAO()
    another_question = question_dao.create(db, obj_in=QuestionCreate(
        title="Another Question",
        question_text="Another question text.",
        instructions="Test instructions for another question.",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.GENERAL,
        created_by_user_id=test_interview.created_by_user_id
    ))

    iq_asked_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=another_question.id,
        status=InterviewQuestionStatus.ASKED,
        order_index=2,
        question_text_snapshot=another_question.question_text
    )
    interview_question_dao.create(db, obj_in=iq_asked_create)

    pending_results = interview_question_dao.get_by_status(db, interview_id=test_interview.id, status=InterviewQuestionStatus.PENDING)
    asked_results = interview_question_dao.get_by_status(db, interview_id=test_interview.id, status=InterviewQuestionStatus.ASKED)

    assert len(pending_results) == 1
    assert pending_results[0].status == InterviewQuestionStatus.PENDING
    
    assert len(asked_results) == 1
    assert asked_results[0].status == InterviewQuestionStatus.ASKED


def test_get_next_question(db, interview_question_dao, test_interview, test_question):
    """Test that get_next_question returns the pending question with the lowest order_index."""
    # Create a question that is already answered
    answered_question_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=test_question.id,
        status=InterviewQuestionStatus.ANSWERED,
        order_index=0,
        question_text_snapshot=test_question.question_text
    )
    interview_question_dao.create(db, obj_in=answered_question_create)

    # Create the next pending question
    question_dao = QuestionDAO()
    next_q_model = question_dao.create(db, obj_in=QuestionCreate(
        title="Next Question",
        question_text="This should be next.",
        instructions="Test instructions for next question.",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.GENERAL,
        created_by_user_id=test_interview.created_by_user_id
    ))
    next_pending_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=next_q_model.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot=next_q_model.question_text
    )
    interview_question_dao.create(db, obj_in=next_pending_create)

    next_question = interview_question_dao.get_next_question(db, interview_id=test_interview.id)

    assert next_question is not None
    assert isinstance(next_question, InterviewQuestionResponse)
    assert next_question.status == InterviewQuestionStatus.PENDING
    assert next_question.order_index == 1
    assert next_question.question_id == next_q_model.id


def test_mark_as_asked(db, interview_question_dao, test_interview, test_question):
    """Test that mark_as_asked updates the status and asked_at timestamp."""
    iq_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=test_question.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot=test_question.question_text
    )
    created_iq = interview_question_dao.create(db, obj_in=iq_create)

    before_update = datetime.now(timezone.utc)
    result = interview_question_dao.mark_as_asked(db, id=created_iq.id)
    
    assert result is not None
    assert result.status == InterviewQuestionStatus.ASKED
    assert result.asked_at is not None
    assert result.asked_at > before_update


def test_mark_as_answered(db, interview_question_dao, test_interview, test_question):
    """Test that mark_as_answered updates status, answer, analysis, and answered_at."""
    iq_create = InterviewQuestionCreate(
        interview_id=test_interview.id,
        question_id=test_question.id,
        status=InterviewQuestionStatus.ASKED,
        order_index=1,
        question_text_snapshot=test_question.question_text
    )
    created_iq = interview_question_dao.create(db, obj_in=iq_create)

    answer = "The candidate provided this answer."
    ai_analysis = {"sentiment": "positive", "clarity": "high"}
    before_update = datetime.now(timezone.utc)

    result = interview_question_dao.mark_as_answered(db, id=created_iq.id, answer=answer, ai_analysis=ai_analysis)

    assert result is not None
    assert result.status == InterviewQuestionStatus.ANSWERED
    assert result.candidate_answer == answer
    assert result.ai_analysis == ai_analysis
    assert result.answered_at is not None
    assert result.answered_at > before_update
