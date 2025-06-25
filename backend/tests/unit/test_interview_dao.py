"""
Unit tests for InterviewDAO to verify proper database operations and Pydantic object returns.
"""
import pytest
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewResponse
from app.schemas.user import UserCreate
from app.schemas.question import QuestionCreate
from app.models.interview import (
    Interview,
    QuestionImportance,
    QuestionCategory,
)
from app.crud.user import UserDAO
from app.crud.question import QuestionDAO
from app.crud.interview import InterviewDAO


@pytest.fixture
def test_user_id(db):
    """Create a test user and return its ID."""
    user_dao = UserDAO()
    user_create = UserCreate(username="testuser", email="test@example.com", full_name="Test User")
    created_user = user_dao.create(db, obj_in=user_create)
    return created_user.id


def create_test_questions(db, test_user_id, count=3):
    """Helper function to create test questions and return their IDs."""
    question_dao = QuestionDAO()
    question_ids = []

    questions_data = [
        {
            "title": "Criminal Background Check",
            "question_text": "Have you ever been convicted of a crime? Please provide complete details.",
            "importance": QuestionImportance.MANDATORY,
            "category": QuestionCategory.CRIMINAL_BACKGROUND,
        },
        {
            "title": "Drug Use History",
            "question_text": "Have you used illegal drugs in the past 5 years? Please be honest.",
            "importance": QuestionImportance.ASK_ONCE,
            "category": QuestionCategory.DRUG_USE,
        },
        {
            "title": "Ethics Question",
            "question_text": "Describe a time when you faced an ethical dilemma and how you handled it.",
            "importance": QuestionImportance.OPTIONAL,
            "category": QuestionCategory.ETHICS,
        },
    ]

    for i in range(min(count, len(questions_data))):
        question_data = questions_data[i]
        question_create = QuestionCreate(
            title=question_data["title"],
            question_text=question_data["question_text"],
            instructions="Test instructions for this question",
            importance=question_data["importance"],
            category=question_data["category"],
            created_by_user_id=test_user_id,
        )
        created_question = question_dao.create(db, obj_in=question_create)
        question_ids.append(created_question.id)

    return question_ids


def test_interview_dao_create_returns_pydantic_object(db, interview_dao: InterviewDAO, test_user_id: int):
    """Test that InterviewDAO.create returns an InterviewResponse (Pydantic object)."""
    question_ids = create_test_questions(db, test_user_id, count=2)

    interview_create = InterviewCreate(
        job_title="Software Engineer",
        job_description="A test job",
        question_ids=question_ids,
    )

    result = interview_dao.create(db, obj_in=interview_create, created_by_user_id=test_user_id)

    assert isinstance(result, InterviewResponse)
    assert result.job_title == "Software Engineer"
    assert result.id is not None
    assert result.created_at is not None
    assert result.updated_at is not None
    assert result.total_candidates == 0
    assert result.completed_candidates == 0
    assert result.avg_score is None


def test_interview_dao_create_minimal_data(db, interview_dao: InterviewDAO, test_user_id: int):
    """Test creating an interview with minimal required data."""
    question_ids = create_test_questions(db, test_user_id, count=1)

    interview_create = InterviewCreate(
        job_title="Data Analyst",
        question_ids=question_ids,
    )

    result = interview_dao.create(db, obj_in=interview_create, created_by_user_id=test_user_id)

    assert isinstance(result, InterviewResponse)
    assert result.job_title == "Data Analyst"
    assert result.id is not None
    assert result.total_candidates == 0


def test_interview_dao_get_returns_pydantic_object(db, interview_dao: InterviewDAO, test_user_id: int):
    """Test that InterviewDAO.get returns an InterviewResponse (Pydantic object)."""
    question_ids = create_test_questions(db, test_user_id, count=2)
    interview_create = InterviewCreate(
        job_title="Product Manager",
        question_ids=question_ids,
    )
    created_interview = interview_dao.create(db, obj_in=interview_create, created_by_user_id=test_user_id)

    result = interview_dao.get(db, created_interview.id)

    assert isinstance(result, InterviewResponse)
    assert result.job_title == "Product Manager"
    assert result.id == created_interview.id


def test_interview_dao_get_nonexistent_returns_none(db, interview_dao: InterviewDAO):
    """Test that getting a non-existent interview returns None."""
    result = interview_dao.get(db, 99999)
    assert result is None


def test_interview_dao_get_multi_returns_pydantic_objects(db, interview_dao: InterviewDAO, test_user_id: int):
    """Test that InterviewDAO.get_multi returns a list of InterviewResponse objects."""
    question_ids = create_test_questions(db, test_user_id, count=1)

    # Create multiple interviews
    for i in range(3):
        interview_create = InterviewCreate(
            job_title=f"Test Job {i}",
            question_ids=question_ids,
        )
        interview_dao.create(db, obj_in=interview_create, created_by_user_id=test_user_id)

    result = interview_dao.get_multi(db, skip=0, limit=10)

    assert isinstance(result, list)
    assert len(result) >= 3
    for interview in result:
        assert isinstance(interview, InterviewResponse)
        assert interview.id is not None


def test_interview_dao_get_multi_with_pagination(db, interview_dao: InterviewDAO, test_user_id: int):
    """Test pagination in get_multi method."""
    question_ids = create_test_questions(db, test_user_id, count=1)

    # Create 5 interviews
    for i in range(5):
        interview_create = InterviewCreate(
            job_title=f"Paginated Job {i}",
            question_ids=question_ids,
        )
        interview_dao.create(db, obj_in=interview_create, created_by_user_id=test_user_id)

    first_page = interview_dao.get_multi(db, skip=0, limit=2)
    second_page = interview_dao.get_multi(db, skip=2, limit=2)

    assert len(first_page) == 2
    assert len(second_page) == 2

    first_page_ids = {interview.id for interview in first_page}
    second_page_ids = {interview.id for interview in second_page}
    assert first_page_ids.isdisjoint(second_page_ids)


def test_interview_dao_update_returns_pydantic_object(db, interview_dao: InterviewDAO, test_user_id: int):
    """Test that InterviewDAO.update returns an InterviewResponse (Pydantic object)."""
    question_ids = create_test_questions(db, test_user_id, count=1)
    interview_create = InterviewCreate(
        job_title="Update Job",
        question_ids=question_ids,
    )
    created_interview = interview_dao.create(db, obj_in=interview_create, created_by_user_id=test_user_id)

    # Get the SQLAlchemy model for update
    db_interview = db.query(Interview).filter(Interview.id == created_interview.id).first()

    # Update the interview
    interview_update = InterviewUpdate(
        job_title="Updated Job Title",
        instructions="These are updated instructions.",
        avg_score=90,
    )
    result = interview_dao.update(db, db_obj=db_interview, obj_in=interview_update)

    # Verify it returns an InterviewResponse (Pydantic object)
    assert isinstance(result, InterviewResponse)
    assert result.job_title == "Updated Job Title"
    assert result.instructions == "These are updated instructions."
    assert result.avg_score == 90
    assert result.id == created_interview.id


def test_interview_dao_update_partial_fields(db, interview_dao: InterviewDAO, test_user_id: int):
    """Test updating only specific fields."""
    question_ids = create_test_questions(db, test_user_id, count=1)
    interview_create = InterviewCreate(
        job_title="Partial Job",
        question_ids=question_ids,
        instructions="Initial instructions",
    )
    created_interview = interview_dao.create(db, obj_in=interview_create, created_by_user_id=test_user_id)

    # Get the SQLAlchemy model for update
    db_interview = db.query(Interview).filter(Interview.id == created_interview.id).first()

    # Update only the job_title
    interview_update = InterviewUpdate(job_title="Partially Updated Job")
    result = interview_dao.update(db, db_obj=db_interview, obj_in=interview_update)

    # Verify only job_title was updated
    assert result.job_title == "Partially Updated Job"
    assert result.instructions == "Initial instructions"  # Unchanged


def test_interview_dao_delete_existing_interview(db, interview_dao: InterviewDAO, test_user_id: int):
    """Test deleting an existing interview."""
    question_ids = create_test_questions(db, test_user_id, count=1)
    interview_create = InterviewCreate(
        job_title="Delete Job",
        question_ids=question_ids,
    )
    created_interview = interview_dao.create(db, obj_in=interview_create, created_by_user_id=test_user_id)

    # Delete the interview
    result = interview_dao.delete(db, id=created_interview.id)

    # Verify deletion was successful
    assert result is True

    # Verify interview no longer exists
    deleted_interview = interview_dao.get(db, created_interview.id)
    assert deleted_interview is None


def test_interview_dao_delete_nonexistent_interview(db, interview_dao: InterviewDAO):
    """Test deleting a non-existent interview."""
    result = interview_dao.delete(db, id=99999)
    assert result is False
