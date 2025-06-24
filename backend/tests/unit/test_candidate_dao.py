"""
Unit tests for CandidateDAO to verify proper database operations and Pydantic object returns.
"""
import pytest
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.models.candidate import Candidate
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


def test_candidate_dao_create_returns_pydantic_object(db, candidate_dao, test_user_id):
    """Test that CandidateDAO.create returns a CandidateResponse (Pydantic object)."""
    candidate_create = CandidateCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+1234567890"
    )

    result = candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Verify it returns a CandidateResponse (Pydantic object)
    assert isinstance(result, CandidateResponse)
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    assert result.phone == "+1234567890"
    assert result.id is not None
    assert result.created_at is not None
    assert result.updated_at is not None


def test_candidate_dao_create_without_phone(db, candidate_dao, test_user_id):
    """Test creating a candidate without phone number."""
    candidate_create = CandidateCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com"
    )

    result = candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    assert isinstance(result, CandidateResponse)
    assert result.first_name == "Jane"
    assert result.last_name == "Smith"
    assert result.email == "jane.smith@example.com"
    assert result.phone is None
    assert result.id is not None


def test_candidate_dao_get_returns_pydantic_object(db, candidate_dao, test_user_id):
    """Test that CandidateDAO.get returns a CandidateResponse (Pydantic object)."""
    # Create a candidate first
    candidate_create = CandidateCreate(
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com",
        phone="+1987654321"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Get the candidate by ID
    result = candidate_dao.get(db, created_candidate.id)
    
    # Verify it returns a CandidateResponse (Pydantic object)
    assert isinstance(result, CandidateResponse)
    assert result.first_name == "Alice"
    assert result.last_name == "Johnson"
    assert result.email == "alice.johnson@example.com"
    assert result.phone == "+1987654321"
    assert result.id == created_candidate.id


def test_candidate_dao_get_nonexistent_returns_none(db, candidate_dao):
    """Test that getting a non-existent candidate returns None."""
    result = candidate_dao.get(db, 99999)
    assert result is None


def test_candidate_dao_get_multi_returns_pydantic_objects(db, candidate_dao, test_user_id):
    """Test that CandidateDAO.get_multi returns a list of CandidateResponse objects."""
    # Create multiple candidates
    candidates_data = [
        {"first_name": "Bob", "last_name": "Wilson", "email": "bob.wilson@example.com"},
        {"first_name": "Carol", "last_name": "Brown", "email": "carol.brown@example.com"},
        {"first_name": "David", "last_name": "Davis", "email": "david.davis@example.com"}
    ]

    for candidate_data in candidates_data:
        candidate_create = CandidateCreate(**candidate_data)
        candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Get all candidates
    result = candidate_dao.get_multi(db, skip=0, limit=10)
    
    # Verify it returns a list of CandidateResponse objects
    assert isinstance(result, list)
    assert len(result) == 3
    for candidate in result:
        assert isinstance(candidate, CandidateResponse)
        assert candidate.id is not None
        assert candidate.first_name is not None
        assert candidate.last_name is not None
        assert candidate.email is not None


def test_candidate_dao_get_multi_with_pagination(db, candidate_dao, test_user_id):
    """Test pagination in get_multi method."""
    # Create 5 candidates
    for i in range(5):
        candidate_create = CandidateCreate(
            first_name=f"User{i}",
            last_name=f"Test{i}",
            email=f"user{i}@example.com"
        )
        candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Test pagination
    first_page = candidate_dao.get_multi(db, skip=0, limit=2)
    second_page = candidate_dao.get_multi(db, skip=2, limit=2)
    
    assert len(first_page) == 2
    assert len(second_page) == 2
    
    # Ensure different candidates on different pages
    first_page_ids = {candidate.id for candidate in first_page}
    second_page_ids = {candidate.id for candidate in second_page}
    assert first_page_ids.isdisjoint(second_page_ids)


def test_candidate_dao_update_returns_pydantic_object(db, candidate_dao, test_user_id):
    """Test that CandidateDAO.update returns a CandidateResponse (Pydantic object)."""
    # Create a candidate first
    candidate_create = CandidateCreate(
        first_name="Original",
        last_name="Name",
        email="original@example.com",
        phone="+1111111111"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Get the SQLAlchemy model for update
    db_candidate = db.query(Candidate).filter(Candidate.id == created_candidate.id).first()
    
    # Update the candidate
    candidate_update = CandidateUpdate(
        first_name="Updated",
        phone="+2222222222"
    )
    result = candidate_dao.update(db, db_obj=db_candidate, obj_in=candidate_update)
    
    # Verify it returns a CandidateResponse (Pydantic object)
    assert isinstance(result, CandidateResponse)
    assert result.first_name == "Updated"
    assert result.last_name == "Name"  # Unchanged
    assert result.email == "original@example.com"  # Unchanged
    assert result.phone == "+2222222222"
    assert result.id == created_candidate.id


def test_candidate_dao_update_partial_fields(db, candidate_dao, test_user_id):
    """Test updating only specific fields."""
    # Create a candidate
    candidate_create = CandidateCreate(
        first_name="Test",
        last_name="User",
        email="test.user@example.com",
        phone="+1234567890"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Get the SQLAlchemy model for update
    db_candidate = db.query(Candidate).filter(Candidate.id == created_candidate.id).first()
    
    # Update only the email
    candidate_update = CandidateUpdate(email="updated.email@example.com")
    result = candidate_dao.update(db, db_obj=db_candidate, obj_in=candidate_update)
    
    # Verify only email was updated
    assert result.first_name == "Test"  # Unchanged
    assert result.last_name == "User"  # Unchanged
    assert result.email == "updated.email@example.com"  # Updated
    assert result.phone == "+1234567890"  # Unchanged


def test_candidate_dao_delete_existing_candidate(db, candidate_dao, test_user_id):
    """Test deleting an existing candidate."""
    # Create a candidate
    candidate_create = CandidateCreate(
        first_name="ToDelete",
        last_name="User",
        email="todelete@example.com"
    )
    created_candidate = candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Delete the candidate
    result = candidate_dao.delete(db, id=created_candidate.id)
    
    # Verify deletion was successful
    assert result is True
    
    # Verify candidate no longer exists
    deleted_candidate = candidate_dao.get(db, created_candidate.id)
    assert deleted_candidate is None


def test_candidate_dao_delete_nonexistent_candidate(db, candidate_dao):
    """Test deleting a non-existent candidate."""
    result = candidate_dao.delete(db, id=99999)
    assert result is False


def test_candidate_dao_get_by_email_returns_pydantic_object(db, candidate_dao, test_user_id):
    """Test that CandidateDAO.get_by_email returns a CandidateResponse (Pydantic object)."""
    # Create a candidate
    candidate_create = CandidateCreate(
        first_name="Email",
        last_name="Test",
        email="email.test@example.com"
    )
    candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Get candidate by email
    result = candidate_dao.get_by_email(db, "email.test@example.com")
    
    # Verify it returns a CandidateResponse (Pydantic object)
    assert isinstance(result, CandidateResponse)
    assert result.email == "email.test@example.com"
    assert result.first_name == "Email"
    assert result.last_name == "Test"


def test_candidate_dao_get_by_email_nonexistent(db, candidate_dao):
    """Test getting candidate by non-existent email."""
    result = candidate_dao.get_by_email(db, "nonexistent@example.com")
    assert result is None


def test_candidate_dao_search_by_name_returns_pydantic_objects(db, candidate_dao, test_user_id):
    """Test that CandidateDAO.search_by_name returns CandidateResponse objects."""
    # Create candidates with different names
    candidates_data = [
        {"first_name": "John", "last_name": "Smith", "email": "john.smith@example.com"},
        {"first_name": "Jane", "last_name": "Johnson", "email": "jane.johnson@example.com"},
        {"first_name": "Bob", "last_name": "Smith", "email": "bob.smith@example.com"}
    ]

    for candidate_data in candidates_data:
        candidate_create = CandidateCreate(**candidate_data)
        candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Search by last name
    result = candidate_dao.search_by_name(db, "Smith")
    
    # Verify it returns CandidateResponse objects
    assert isinstance(result, list)
    assert len(result) == 2  # John Smith and Bob Smith
    for candidate in result:
        assert isinstance(candidate, CandidateResponse)
        assert "Smith" in candidate.last_name


def test_candidate_dao_search_by_name_case_insensitive(db, candidate_dao, test_user_id):
    """Test that name search is case insensitive."""
    # Create a candidate
    candidate_create = CandidateCreate(
        first_name="CaseTest",
        last_name="User",
        email="casetest@example.com"
    )
    candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=test_user_id)
    
    # Search with different cases
    result_lower = candidate_dao.search_by_name(db, "casetest")
    result_upper = candidate_dao.search_by_name(db, "CASETEST")
    result_mixed = candidate_dao.search_by_name(db, "CaseTeSt")
    
    # All should return the same candidate
    assert len(result_lower) == 1
    assert len(result_upper) == 1
    assert len(result_mixed) == 1
    assert result_lower[0].first_name == "CaseTest"
    assert result_upper[0].first_name == "CaseTest"
    assert result_mixed[0].first_name == "CaseTest"
