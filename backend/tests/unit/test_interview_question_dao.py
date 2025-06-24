"""
Unit tests for InterviewQuestionDAO to verify proper database operations and Pydantic object returns.
"""
import pytest
from datetime import datetime, timezone
from app.schemas.interview_question import InterviewQuestionCreate, InterviewQuestionUpdate, InterviewQuestionResponse
from app.schemas.interview import InterviewCreate
from app.schemas.question import QuestionCreate
from app.schemas.candidate import CandidateCreate
from app.schemas.job import JobCreate
from app.schemas.user import UserCreate
from app.models.interview import InterviewQuestion, InterviewQuestionStatus, QuestionImportance, QuestionCategory


def test_interview_question_dao_create_returns_pydantic_object(db, interview_question_dao, interview_dao, question_dao, candidate_dao, job_dao, user_dao):
    """Test that InterviewQuestionDAO.create returns an InterviewQuestionResponse (Pydantic object)."""
    # Create dependencies first
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    candidate_create = CandidateCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create)
    
    job_create = JobCreate(
        title="Software Engineer",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    interview_create = InterviewCreate(
        candidate_id=created_candidate.id,
        job_id=created_job.id
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)
    
    question_create = QuestionCreate(
        title="Criminal Background",
        question_text="Have you ever been convicted of a crime?",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.CRIMINAL_BACKGROUND,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)
    
    # Create an interview question
    interview_question_create = InterviewQuestionCreate(
        interview_id=created_interview.id,
        question_id=created_question.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot="Have you ever been convicted of a crime?"
    )
    
    result = interview_question_dao.create(db, obj_in=interview_question_create)
    
    # Verify it returns an InterviewQuestionResponse (Pydantic object)
    assert isinstance(result, InterviewQuestionResponse)
    assert result.interview_id == created_interview.id
    assert result.question_id == created_question.id
    assert result.status == InterviewQuestionStatus.PENDING
    assert result.order_index == 1
    assert result.question_text_snapshot == "Have you ever been convicted of a crime?"
    assert result.id is not None
    assert result.candidate_answer is None  # Not set initially
    assert result.ai_analysis is None
    assert result.follow_up_questions is None


def test_interview_question_dao_get_returns_pydantic_object(db, interview_question_dao, interview_dao, question_dao, candidate_dao, job_dao, user_dao):
    """Test that InterviewQuestionDAO.get returns an InterviewQuestionResponse (Pydantic object)."""
    # Create dependencies and interview question
    user_create = UserCreate(
        username="testuser2",
        email="test2@example.com",
        full_name="Test User 2"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    candidate_create = CandidateCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create)
    
    job_create = JobCreate(
        title="Data Analyst",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    interview_create = InterviewCreate(
        candidate_id=created_candidate.id,
        job_id=created_job.id
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)
    
    question_create = QuestionCreate(
        title="Drug Use",
        question_text="Have you used illegal drugs?",
        importance=QuestionImportance.ASK_ONCE,
        category=QuestionCategory.DRUG_USE,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)
    
    interview_question_create = InterviewQuestionCreate(
        interview_id=created_interview.id,
        question_id=created_question.id,
        status=InterviewQuestionStatus.ASKED,
        order_index=2,
        question_text_snapshot="Have you used illegal drugs?"
    )
    created_interview_question = interview_question_dao.create(db, obj_in=interview_question_create)
    
    # Get the interview question by ID
    result = interview_question_dao.get(db, created_interview_question.id)
    
    # Verify it returns an InterviewQuestionResponse (Pydantic object)
    assert isinstance(result, InterviewQuestionResponse)
    assert result.interview_id == created_interview.id
    assert result.question_id == created_question.id
    assert result.status == InterviewQuestionStatus.ASKED
    assert result.order_index == 2
    assert result.id == created_interview_question.id


def test_interview_question_dao_get_nonexistent_returns_none(db, interview_question_dao):
    """Test that getting a non-existent interview question returns None."""
    result = interview_question_dao.get(db, 99999)
    assert result is None


def test_interview_question_dao_get_multi_returns_pydantic_objects(db, interview_question_dao, interview_dao, question_dao, candidate_dao, job_dao, user_dao):
    """Test that InterviewQuestionDAO.get_multi returns a list of InterviewQuestionResponse objects."""
    # Create dependencies
    user_create = UserCreate(
        username="testuser3",
        email="test3@example.com",
        full_name="Test User 3"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    candidate_create = CandidateCreate(
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create)
    
    job_create = JobCreate(
        title="Product Manager",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    interview_create = InterviewCreate(
        candidate_id=created_candidate.id,
        job_id=created_job.id
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)
    
    # Create multiple questions and interview questions
    for i in range(3):
        question_create = QuestionCreate(
            title=f"Question {i}",
            question_text=f"This is a detailed question text for question number {i} with sufficient length",
            importance=QuestionImportance.ASK_ONCE,
            category=QuestionCategory.ETHICS,
            created_by_user_id=created_user.id
        )
        created_question = question_dao.create(db, obj_in=question_create)

        interview_question_create = InterviewQuestionCreate(
            interview_id=created_interview.id,
            question_id=created_question.id,
            status=InterviewQuestionStatus.PENDING,
            order_index=i + 1,
            question_text_snapshot=f"This is a detailed question text for question number {i} with sufficient length"
        )
        interview_question_dao.create(db, obj_in=interview_question_create)
    
    # Get all interview questions
    result = interview_question_dao.get_multi(db, skip=0, limit=10)
    
    # Verify it returns a list of InterviewQuestionResponse objects
    assert isinstance(result, list)
    assert len(result) == 3
    for interview_question in result:
        assert isinstance(interview_question, InterviewQuestionResponse)
        assert interview_question.id is not None
        assert interview_question.interview_id == created_interview.id


def test_interview_question_dao_get_multi_with_pagination(db, interview_question_dao, interview_dao, question_dao, candidate_dao, job_dao, user_dao):
    """Test pagination in get_multi method."""
    # Create dependencies
    user_create = UserCreate(
        username="testuser4",
        email="test4@example.com",
        full_name="Test User 4"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    candidate_create = CandidateCreate(
        first_name="Bob",
        last_name="Wilson",
        email="bob.wilson@example.com"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create)
    
    job_create = JobCreate(
        title="Test Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    interview_create = InterviewCreate(
        candidate_id=created_candidate.id,
        job_id=created_job.id
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)
    
    # Create 5 interview questions
    for i in range(5):
        question_create = QuestionCreate(
            title=f"Question {i}",
            question_text=f"This is a detailed question text for question number {i} with sufficient length",
            importance=QuestionImportance.OPTIONAL,
            category=QuestionCategory.ETHICS,
            created_by_user_id=created_user.id
        )
        created_question = question_dao.create(db, obj_in=question_create)

        interview_question_create = InterviewQuestionCreate(
            interview_id=created_interview.id,
            question_id=created_question.id,
            status=InterviewQuestionStatus.PENDING,
            order_index=i + 1,
            question_text_snapshot=f"This is a detailed question text for question number {i} with sufficient length"
        )
        interview_question_dao.create(db, obj_in=interview_question_create)
    
    # Test pagination
    first_page = interview_question_dao.get_multi(db, skip=0, limit=2)
    second_page = interview_question_dao.get_multi(db, skip=2, limit=2)
    
    assert len(first_page) == 2
    assert len(second_page) == 2
    
    # Ensure different interview questions on different pages
    first_page_ids = {iq.id for iq in first_page}
    second_page_ids = {iq.id for iq in second_page}
    assert first_page_ids.isdisjoint(second_page_ids)


def test_interview_question_dao_update_returns_pydantic_object(db, interview_question_dao, interview_dao, question_dao, candidate_dao, job_dao, user_dao):
    """Test that InterviewQuestionDAO.update returns an InterviewQuestionResponse (Pydantic object)."""
    # Create dependencies and interview question
    user_create = UserCreate(
        username="testuser5",
        email="test5@example.com",
        full_name="Test User 5"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    candidate_create = CandidateCreate(
        first_name="Update",
        last_name="Test",
        email="update.test@example.com"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create)
    
    job_create = JobCreate(
        title="Update Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    interview_create = InterviewCreate(
        candidate_id=created_candidate.id,
        job_id=created_job.id
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)
    
    question_create = QuestionCreate(
        title="Update Question",
        question_text="This is a comprehensive update question text with sufficient length for validation",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.DISMISSALS,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)

    interview_question_create = InterviewQuestionCreate(
        interview_id=created_interview.id,
        question_id=created_question.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot="This is a comprehensive update question text with sufficient length for validation"
    )
    created_interview_question = interview_question_dao.create(db, obj_in=interview_question_create)
    
    # Get the SQLAlchemy model for update
    db_interview_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == created_interview_question.id
    ).first()
    
    # Update the interview question
    asked_at = datetime.now(timezone.utc)
    answered_at = datetime.now(timezone.utc)
    interview_question_update = InterviewQuestionUpdate(
        status=InterviewQuestionStatus.ANSWERED,
        candidate_answer="No, I have never been dismissed from a job.",
        ai_analysis={"sentiment": "positive", "confidence": 0.95},
        follow_up_questions={"questions": ["Can you provide references?"]},
        asked_at=asked_at,
        answered_at=answered_at
    )
    result = interview_question_dao.update(db, db_obj=db_interview_question, obj_in=interview_question_update)
    
    # Verify it returns an InterviewQuestionResponse (Pydantic object)
    assert isinstance(result, InterviewQuestionResponse)
    assert result.status == InterviewQuestionStatus.ANSWERED
    assert result.candidate_answer == "No, I have never been dismissed from a job."
    assert result.ai_analysis == {"sentiment": "positive", "confidence": 0.95}
    assert result.follow_up_questions == {"questions": ["Can you provide references?"]}
    # Compare datetime without timezone info since DB may strip timezone
    assert result.asked_at is not None
    assert result.asked_at.replace(tzinfo=None) == asked_at.replace(tzinfo=None)
    assert result.answered_at is not None
    assert result.answered_at.replace(tzinfo=None) == answered_at.replace(tzinfo=None)
    assert result.interview_id == created_interview.id  # Unchanged
    assert result.question_id == created_question.id  # Unchanged
    assert result.order_index == 1  # Unchanged
    assert result.id == created_interview_question.id


def test_interview_question_dao_update_partial_fields(db, interview_question_dao, interview_dao, question_dao, candidate_dao, job_dao, user_dao):
    """Test updating only specific fields."""
    # Create dependencies and interview question
    user_create = UserCreate(
        username="testuser6",
        email="test6@example.com",
        full_name="Test User 6"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    candidate_create = CandidateCreate(
        first_name="Partial",
        last_name="Update",
        email="partial.update@example.com"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create)
    
    job_create = JobCreate(
        title="Partial Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    interview_create = InterviewCreate(
        candidate_id=created_candidate.id,
        job_id=created_job.id
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)
    
    question_create = QuestionCreate(
        title="Partial Question",
        question_text="This is a comprehensive partial question text with sufficient length for validation",
        importance=QuestionImportance.ASK_ONCE,
        category=QuestionCategory.ETHICS,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)

    interview_question_create = InterviewQuestionCreate(
        interview_id=created_interview.id,
        question_id=created_question.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot="This is a comprehensive partial question text with sufficient length for validation"
    )
    created_interview_question = interview_question_dao.create(db, obj_in=interview_question_create)
    
    # Get the SQLAlchemy model for update
    db_interview_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == created_interview_question.id
    ).first()
    
    # Update only the status
    interview_question_update = InterviewQuestionUpdate(status=InterviewQuestionStatus.ASKED)
    result = interview_question_dao.update(db, db_obj=db_interview_question, obj_in=interview_question_update)
    
    # Verify only status was updated
    assert result.status == InterviewQuestionStatus.ASKED  # Updated
    assert result.candidate_answer is None  # Unchanged
    assert result.ai_analysis is None  # Unchanged
    assert result.follow_up_questions is None  # Unchanged
    assert result.asked_at is None  # Unchanged
    assert result.answered_at is None  # Unchanged
    assert result.interview_id == created_interview.id  # Unchanged
    assert result.question_id == created_question.id  # Unchanged


def test_interview_question_dao_delete_existing_interview_question(db, interview_question_dao, interview_dao, question_dao, candidate_dao, job_dao, user_dao):
    """Test deleting an existing interview question."""
    # Create dependencies and interview question
    user_create = UserCreate(
        username="testuser7",
        email="test7@example.com",
        full_name="Test User 7"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    candidate_create = CandidateCreate(
        first_name="Delete",
        last_name="Test",
        email="delete.test@example.com"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create)
    
    job_create = JobCreate(
        title="Delete Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    interview_create = InterviewCreate(
        candidate_id=created_candidate.id,
        job_id=created_job.id
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)
    
    question_create = QuestionCreate(
        title="Delete Question",
        question_text="This is a comprehensive delete question text with sufficient length for validation",
        importance=QuestionImportance.OPTIONAL,
        category=QuestionCategory.ETHICS,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)

    interview_question_create = InterviewQuestionCreate(
        interview_id=created_interview.id,
        question_id=created_question.id,
        status=InterviewQuestionStatus.PENDING,
        order_index=1,
        question_text_snapshot="This is a comprehensive delete question text with sufficient length for validation"
    )
    created_interview_question = interview_question_dao.create(db, obj_in=interview_question_create)
    
    # Delete the interview question
    result = interview_question_dao.delete(db, id=created_interview_question.id)
    
    # Verify deletion was successful
    assert result is True
    
    # Verify interview question no longer exists
    deleted_interview_question = interview_question_dao.get(db, created_interview_question.id)
    assert deleted_interview_question is None


def test_interview_question_dao_delete_nonexistent_interview_question(db, interview_question_dao):
    """Test deleting a non-existent interview question."""
    result = interview_question_dao.delete(db, id=99999)
    assert result is False
