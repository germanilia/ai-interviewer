"""
Unit tests for InterviewDAO to verify proper database operations and Pydantic object returns.
"""
import pytest
from datetime import datetime, timezone
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewResponse
from app.schemas.candidate import CandidateCreate
from app.schemas.job import JobCreate
from app.schemas.user import UserCreate
from app.models.interview import Interview, InterviewStatus, IntegrityScore, RiskLevel


def test_interview_dao_create_returns_pydantic_object(db, interview_dao, candidate_dao, job_dao, user_dao):
    """Test that InterviewDAO.create returns an InterviewResponse (Pydantic object)."""
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
    
    # Create an interview
    interview_date = datetime.now(timezone.utc)
    interview_create = InterviewCreate(
        candidate_id=created_candidate.id,
        job_id=created_job.id,
        status=InterviewStatus.IN_PROGRESS,
        interview_date=interview_date
    )

    result = interview_dao.create(db, obj_in=interview_create)

    # Verify it returns an InterviewResponse (Pydantic object)
    assert isinstance(result, InterviewResponse)
    assert result.candidate_id == created_candidate.id
    assert result.job_id == created_job.id
    assert result.status == InterviewStatus.IN_PROGRESS
    # Compare datetime without timezone info since DB may strip timezone
    assert result.interview_date is not None
    assert result.interview_date.replace(tzinfo=None) == interview_date.replace(tzinfo=None)
    assert result.id is not None
    assert result.created_at is not None
    assert result.updated_at is not None
    assert result.score is None  # Not set initially
    assert result.integrity_score is None
    assert result.risk_level is None


def test_interview_dao_create_minimal_data(db, interview_dao, candidate_dao, job_dao, user_dao):
    """Test creating an interview with minimal required data."""
    # Create dependencies
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
    
    # Create interview with minimal data
    interview_create = InterviewCreate(
        candidate_id=created_candidate.id,
        job_id=created_job.id
    )
    
    result = interview_dao.create(db, obj_in=interview_create)
    
    assert isinstance(result, InterviewResponse)
    assert result.candidate_id == created_candidate.id
    assert result.job_id == created_job.id
    assert result.status == InterviewStatus.PENDING  # Default status
    assert result.interview_date is None
    assert result.id is not None


def test_interview_dao_get_returns_pydantic_object(db, interview_dao, candidate_dao, job_dao, user_dao):
    """Test that InterviewDAO.get returns an InterviewResponse (Pydantic object)."""
    # Create dependencies and interview
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
        job_id=created_job.id,
        status=InterviewStatus.IN_PROGRESS
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)
    
    # Get the interview by ID
    result = interview_dao.get(db, created_interview.id)
    
    # Verify it returns an InterviewResponse (Pydantic object)
    assert isinstance(result, InterviewResponse)
    assert result.candidate_id == created_candidate.id
    assert result.job_id == created_job.id
    assert result.status == InterviewStatus.IN_PROGRESS
    assert result.id == created_interview.id


def test_interview_dao_get_nonexistent_returns_none(db, interview_dao):
    """Test that getting a non-existent interview returns None."""
    result = interview_dao.get(db, 99999)
    assert result is None


def test_interview_dao_get_multi_returns_pydantic_objects(db, interview_dao, candidate_dao, job_dao, user_dao):
    """Test that InterviewDAO.get_multi returns a list of InterviewResponse objects."""
    # Create dependencies
    user_create = UserCreate(
        username="testuser4",
        email="test4@example.com",
        full_name="Test User 4"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create multiple candidates and jobs
    candidates = []
    for i in range(3):
        candidate_create = CandidateCreate(
            first_name=f"Candidate{i}",
            last_name=f"Test{i}",
            email=f"candidate{i}@example.com"
        )
        candidates.append(candidate_dao.create(db, obj_in=candidate_create))
    
    job_create = JobCreate(
        title="Test Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Create multiple interviews
    for candidate in candidates:
        interview_create = InterviewCreate(
            candidate_id=candidate.id,
            job_id=created_job.id,
            status=InterviewStatus.PENDING
        )
        interview_dao.create(db, obj_in=interview_create)
    
    # Get all interviews
    result = interview_dao.get_multi(db, skip=0, limit=10)
    
    # Verify it returns a list of InterviewResponse objects
    assert isinstance(result, list)
    assert len(result) == 3
    for interview in result:
        assert isinstance(interview, InterviewResponse)
        assert interview.id is not None
        assert interview.job_id == created_job.id


def test_interview_dao_get_multi_with_pagination(db, interview_dao, candidate_dao, job_dao, user_dao):
    """Test pagination in get_multi method."""
    # Create dependencies
    user_create = UserCreate(
        username="testuser5",
        email="test5@example.com",
        full_name="Test User 5"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Test Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Create 5 interviews
    for i in range(5):
        candidate_create = CandidateCreate(
            first_name=f"Candidate{i}",
            last_name=f"Test{i}",
            email=f"candidate{i}@example.com"
        )
        created_candidate = candidate_dao.create(db, obj_in=candidate_create)
        
        interview_create = InterviewCreate(
            candidate_id=created_candidate.id,
            job_id=created_job.id
        )
        interview_dao.create(db, obj_in=interview_create)
    
    # Test pagination
    first_page = interview_dao.get_multi(db, skip=0, limit=2)
    second_page = interview_dao.get_multi(db, skip=2, limit=2)
    
    assert len(first_page) == 2
    assert len(second_page) == 2
    
    # Ensure different interviews on different pages
    first_page_ids = {interview.id for interview in first_page}
    second_page_ids = {interview.id for interview in second_page}
    assert first_page_ids.isdisjoint(second_page_ids)


def test_interview_dao_update_returns_pydantic_object(db, interview_dao, candidate_dao, job_dao, user_dao):
    """Test that InterviewDAO.update returns an InterviewResponse (Pydantic object)."""
    # Create dependencies and interview
    user_create = UserCreate(
        username="testuser6",
        email="test6@example.com",
        full_name="Test User 6"
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
        job_id=created_job.id,
        status=InterviewStatus.PENDING
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)
    
    # Get the SQLAlchemy model for update
    db_interview = db.query(Interview).filter(Interview.id == created_interview.id).first()
    
    # Update the interview
    completed_at = datetime.now(timezone.utc)
    interview_update = InterviewUpdate(
        status=InterviewStatus.COMPLETED,
        score=85,
        integrity_score=IntegrityScore.HIGH,
        risk_level=RiskLevel.LOW,
        completed_at=completed_at,
        report_summary="Candidate performed well in the interview."
    )
    result = interview_dao.update(db, db_obj=db_interview, obj_in=interview_update)
    
    # Verify it returns an InterviewResponse (Pydantic object)
    assert isinstance(result, InterviewResponse)
    assert result.status == InterviewStatus.COMPLETED
    assert result.score == 85
    assert result.integrity_score == IntegrityScore.HIGH
    assert result.risk_level == RiskLevel.LOW
    # Compare datetime without timezone info since DB may strip timezone
    assert result.completed_at is not None
    assert result.completed_at.replace(tzinfo=None) == completed_at.replace(tzinfo=None)
    assert result.report_summary == "Candidate performed well in the interview."
    assert result.candidate_id == created_candidate.id  # Unchanged
    assert result.job_id == created_job.id  # Unchanged
    assert result.id == created_interview.id


def test_interview_dao_update_partial_fields(db, interview_dao, candidate_dao, job_dao, user_dao):
    """Test updating only specific fields."""
    # Create dependencies and interview
    user_create = UserCreate(
        username="testuser7",
        email="test7@example.com",
        full_name="Test User 7"
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
        job_id=created_job.id,
        status=InterviewStatus.PENDING
    )
    created_interview = interview_dao.create(db, obj_in=interview_create)

    # Get the SQLAlchemy model for update
    db_interview = db.query(Interview).filter(Interview.id == created_interview.id).first()

    # Update only the status
    interview_update = InterviewUpdate(status=InterviewStatus.IN_PROGRESS)
    result = interview_dao.update(db, db_obj=db_interview, obj_in=interview_update)

    # Verify only status was updated
    assert result.status == InterviewStatus.IN_PROGRESS  # Updated
    assert result.score is None  # Unchanged
    assert result.integrity_score is None  # Unchanged
    assert result.risk_level is None  # Unchanged
    assert result.candidate_id == created_candidate.id  # Unchanged
    assert result.job_id == created_job.id  # Unchanged


def test_interview_dao_delete_existing_interview(db, interview_dao, candidate_dao, job_dao, user_dao):
    """Test deleting an existing interview."""
    # Create dependencies and interview
    user_create = UserCreate(
        username="testuser8",
        email="test8@example.com",
        full_name="Test User 8"
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
    
    # Delete the interview
    result = interview_dao.delete(db, id=created_interview.id)
    
    # Verify deletion was successful
    assert result is True
    
    # Verify interview no longer exists
    deleted_interview = interview_dao.get(db, created_interview.id)
    assert deleted_interview is None


def test_interview_dao_delete_nonexistent_interview(db, interview_dao):
    """Test deleting a non-existent interview."""
    result = interview_dao.delete(db, id=99999)
    assert result is False
