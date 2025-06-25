"""
Unit tests for CandidateService to verify proper dependency injection and business logic.
"""
import pytest
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse, CandidateListResponse
from app.services.candidate_service import CandidateService
from app.crud.user import UserDAO
from app.schemas.user import UserCreate


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


def test_candidate_service_dependency_injection(candidate_dao):
    """Test that CandidateService properly accepts CandidateDAO dependency."""
    service = CandidateService(candidate_dao)
    assert service.candidate_dao is candidate_dao


def test_candidate_service_create_candidate_returns_pydantic(db, candidate_service, test_user_id):
    """Test that CandidateService.create_candidate returns CandidateResponse."""
    candidate_create = CandidateCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1234567890",
        interview_id=None,
        pass_key=None
    )

    result = candidate_service.create_candidate(db, candidate_create, test_user_id)
    
    assert isinstance(result, CandidateResponse)
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    assert result.phone == "+1234567890"
    assert result.id is not None


def test_candidate_service_create_candidate_duplicate_email_raises_error(db, candidate_service, test_user_id):
    """Test that creating candidate with duplicate email raises ValueError."""
    candidate_create = CandidateCreate(
        first_name="John",
        last_name="Doe",
        email="duplicate@example.com",
        interview_id=None,
        pass_key=None
    )

    # Create first candidate
    candidate_service.create_candidate(db, candidate_create, test_user_id)

    # Try to create second candidate with same email
    duplicate_candidate = CandidateCreate(
        first_name="Jane",
        last_name="Smith",
        email="duplicate@example.com",
        interview_id=None,
        pass_key=None
    )

    with pytest.raises(ValueError, match="Email already exists"):
        candidate_service.create_candidate(db, duplicate_candidate, test_user_id)


def test_candidate_service_get_candidate_by_id_returns_pydantic(db, candidate_service, test_user_id):
    """Test that CandidateService.get_candidate_by_id returns CandidateResponse."""
    # Create candidate first
    candidate_create = CandidateCreate(
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com",
        interview_id=None,
        pass_key=None
    )
    created_candidate = candidate_service.create_candidate(db, candidate_create, test_user_id)
    
    # Get candidate by ID
    result = candidate_service.get_candidate_by_id(db, created_candidate.id)
    
    assert isinstance(result, CandidateResponse)
    assert result.id == created_candidate.id
    assert result.first_name == "Alice"
    assert result.last_name == "Johnson"


def test_candidate_service_get_candidate_by_id_nonexistent_returns_none(db, candidate_service):
    """Test that getting non-existent candidate returns None."""
    result = candidate_service.get_candidate_by_id(db, 99999)
    assert result is None


def test_candidate_service_get_candidates_returns_paginated_response(db, candidate_service, test_user_id):
    """Test that CandidateService.get_candidates returns CandidateListResponse."""
    # Create multiple candidates
    candidates_data = [
        {"first_name": "Bob", "last_name": "Wilson", "email": "bob.wilson@example.com", "interview_id": None, "pass_key": None},
        {"first_name": "Carol", "last_name": "Brown", "email": "carol.brown@example.com", "interview_id": None, "pass_key": None},
        {"first_name": "David", "last_name": "Davis", "email": "david.davis@example.com", "interview_id": None, "pass_key": None}
    ]

    for candidate_data in candidates_data:
        candidate_create = CandidateCreate(**candidate_data)
        candidate_service.create_candidate(db, candidate_create, test_user_id)
    
    # Get candidates with pagination
    result = candidate_service.get_candidates(db, page=1, page_size=2)
    
    assert isinstance(result, CandidateListResponse)
    assert len(result.items) == 2
    assert result.total == 3
    assert result.page == 1
    assert result.page_size == 2
    assert result.total_pages == 2
    
    for candidate in result.items:
        assert isinstance(candidate, CandidateResponse)


def test_candidate_service_get_candidates_with_search(db, candidate_service, test_user_id):
    """Test that CandidateService.get_candidates supports search functionality."""
    # Create candidates with different names
    candidates_data = [
        {"first_name": "John", "last_name": "Smith", "email": "john.smith@example.com", "interview_id": None, "pass_key": None},
        {"first_name": "Jane", "last_name": "Johnson", "email": "jane.johnson@example.com", "interview_id": None, "pass_key": None},
        {"first_name": "Bob", "last_name": "Smith", "email": "bob.smith@example.com", "interview_id": None, "pass_key": None}
    ]

    for candidate_data in candidates_data:
        candidate_create = CandidateCreate(**candidate_data)
        candidate_service.create_candidate(db, candidate_create, test_user_id)
    
    # Search by last name
    result = candidate_service.get_candidates(db, page=1, page_size=10, search="Smith")
    
    assert isinstance(result, CandidateListResponse)
    assert len(result.items) == 2  # John Smith and Bob Smith
    assert result.total == 2
    
    for candidate in result.items:
        assert "Smith" in candidate.last_name


def test_candidate_service_get_candidates_pagination_validation(db, candidate_service):
    """Test that pagination parameters are validated correctly."""
    # Test invalid page number (should default to 1)
    result = candidate_service.get_candidates(db, page=0, page_size=10)
    assert result.page == 1
    
    # Test invalid page size (should default to 10)
    result = candidate_service.get_candidates(db, page=1, page_size=0)
    assert result.page_size == 10
    
    # Test page size too large (should default to 10)
    result = candidate_service.get_candidates(db, page=1, page_size=200)
    assert result.page_size == 10


def test_candidate_service_get_candidate_by_email_returns_pydantic(db, candidate_service, test_user_id):
    """Test that CandidateService.get_candidate_by_email returns CandidateResponse."""
    # Create candidate
    candidate_create = CandidateCreate(
        first_name="Email",
        last_name="Test",
        email="email.test@example.com",
        interview_id=None,
        pass_key=None
    )
    candidate_service.create_candidate(db, candidate_create, test_user_id)
    
    # Get candidate by email
    result = candidate_service.get_candidate_by_email(db, "email.test@example.com")
    
    assert isinstance(result, CandidateResponse)
    assert result.email == "email.test@example.com"
    assert result.first_name == "Email"


def test_candidate_service_get_candidate_by_email_nonexistent_returns_none(db, candidate_service):
    """Test that getting candidate by non-existent email returns None."""
    result = candidate_service.get_candidate_by_email(db, "nonexistent@example.com")
    assert result is None


def test_candidate_service_update_candidate_returns_pydantic(db, candidate_service, test_user_id):
    """Test that CandidateService.update_candidate returns CandidateResponse."""
    # Create candidate first
    candidate_create = CandidateCreate(
        first_name="Original",
        last_name="Name",
        email="original@example.com",
        phone="+1111111111",
        interview_id=None,
        pass_key=None
    )
    created_candidate = candidate_service.create_candidate(db, candidate_create, test_user_id)
    
    # Update candidate
    candidate_update = CandidateUpdate(
        first_name="Updated",
        phone="+2222222222"
    )
    result = candidate_service.update_candidate(db, created_candidate.id, candidate_update)
    
    assert isinstance(result, CandidateResponse)
    assert result.first_name == "Updated"
    assert result.last_name == "Name"  # Unchanged
    assert result.email == "original@example.com"  # Unchanged
    assert result.phone == "+2222222222"
    assert result.id == created_candidate.id


def test_candidate_service_update_candidate_nonexistent_returns_none(db, candidate_service):
    """Test that updating non-existent candidate returns None."""
    candidate_update = CandidateUpdate(first_name="Updated")
    result = candidate_service.update_candidate(db, 99999, candidate_update)
    assert result is None


def test_candidate_service_update_candidate_duplicate_email_raises_error(db, candidate_service, test_user_id):
    """Test that updating candidate with duplicate email raises ValueError."""
    # Create two candidates
    candidate1 = CandidateCreate(
        first_name="First",
        last_name="User",
        email="first@example.com",
        interview_id=None,
        pass_key=None
    )
    candidate2 = CandidateCreate(
        first_name="Second",
        last_name="User",
        email="second@example.com",
        interview_id=None,
        pass_key=None
    )

    created1 = candidate_service.create_candidate(db, candidate1, test_user_id)
    created2 = candidate_service.create_candidate(db, candidate2, test_user_id)
    
    # Try to update second candidate with first candidate's email
    candidate_update = CandidateUpdate(email="first@example.com")
    
    with pytest.raises(ValueError, match="Email already exists"):
        candidate_service.update_candidate(db, created2.id, candidate_update)


def test_candidate_service_delete_candidate_success(db, candidate_service, test_user_id):
    """Test that CandidateService.delete_candidate works correctly."""
    # Create candidate first
    candidate_create = CandidateCreate(
        first_name="Delete",
        last_name="Me",
        email="delete@example.com",
        interview_id=None,
        pass_key=None
    )
    created_candidate = candidate_service.create_candidate(db, candidate_create, test_user_id)
    
    # Delete candidate
    result = candidate_service.delete_candidate(db, created_candidate.id)
    
    assert result is True
    
    # Verify candidate is deleted
    deleted_candidate = candidate_service.get_candidate_by_id(db, created_candidate.id)
    assert deleted_candidate is None


def test_candidate_service_delete_candidate_nonexistent_returns_false(db, candidate_service):
    """Test that deleting non-existent candidate returns False."""
    result = candidate_service.delete_candidate(db, 99999)
    assert result is False


def test_candidate_service_get_candidate_interview_history(db, candidate_service, test_user_id):
    """Test that CandidateService.get_candidate_interview_history returns list."""
    # Create candidate first
    candidate_create = CandidateCreate(
        first_name="History",
        last_name="Test",
        email="history@example.com",
        interview_id=None,
        pass_key=None
    )
    created_candidate = candidate_service.create_candidate(db, candidate_create, test_user_id)

    # Get interview history (should be empty for now)
    result = candidate_service.get_candidate_interview_history(db, created_candidate.id)

    assert isinstance(result, list)
    assert len(result) == 0  # No interviews yet


def test_candidate_service_reset_candidate_interview_success(db, candidate_service, test_user_id):
    """Test that CandidateService.reset_candidate_interview clears interview data."""
    # Create candidate with interview data
    candidate_create = CandidateCreate(
        first_name="Reset",
        last_name="Test",
        email="reset@example.com",
        interview_id=None,
        pass_key=None
    )
    created_candidate = candidate_service.create_candidate(db, candidate_create, test_user_id)

    # Update candidate with interview data
    from datetime import datetime, timezone
    update_data = CandidateUpdate(
        interview_status="completed",
        interview_date=datetime.now(timezone.utc),
        score=85,
        integrity_score="high",
        risk_level="low",
        conversation={"messages": ["test"]},
        report_summary="Test summary",
        risk_indicators=[{"type": "none", "description": "No risks identified"}],
        key_concerns=[{"area": "none", "details": "No concerns"}],
        analysis_notes="Test notes"
    )
    updated_candidate = candidate_service.update_candidate(db, created_candidate.id, update_data)

    # Verify data was set
    assert updated_candidate.interview_status == "completed"
    assert updated_candidate.score == 85
    assert updated_candidate.conversation is not None

    # Reset the candidate
    reset_candidate = candidate_service.reset_candidate_interview(db, created_candidate.id)

    # Verify reset worked
    assert isinstance(reset_candidate, CandidateResponse)
    assert reset_candidate.id == created_candidate.id
    assert reset_candidate.interview_status is None
    assert reset_candidate.interview_date is None
    assert reset_candidate.score is None
    assert reset_candidate.integrity_score is None
    assert reset_candidate.risk_level is None
    assert reset_candidate.conversation is None
    assert reset_candidate.report_summary is None
    assert reset_candidate.risk_indicators is None
    assert reset_candidate.key_concerns is None
    assert reset_candidate.analysis_notes is None


def test_candidate_service_reset_candidate_interview_nonexistent_returns_none(db, candidate_service):
    """Test that resetting nonexistent candidate returns None."""
    result = candidate_service.reset_candidate_interview(db, 99999)
    assert result is None
