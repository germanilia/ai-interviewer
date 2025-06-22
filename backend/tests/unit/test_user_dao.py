"""
Unit tests for UserDAO to verify proper database operations and Pydantic object returns.
"""
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import UserRole


def test_user_dao_create_returns_pydantic_object(db, user_dao):
    """Test that UserDAO.create returns a UserResponse (Pydantic object)."""
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    
    result = user_dao.create(db, obj_in=user_create)
    
    # Verify it returns a UserResponse (Pydantic object)
    assert isinstance(result, UserResponse)
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert result.full_name == "Test User"
    assert result.role == UserRole.ADMIN  # First user becomes admin
    assert result.is_active is True
    assert result.id is not None


def test_user_dao_get_returns_pydantic_object(db, user_dao):
    """Test that UserDAO.get returns a UserResponse (Pydantic object)."""
    # Create a user first
    user_create = UserCreate(
        username="testuser2",
        email="test2@example.com",
        full_name="Test User 2"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Get the user by ID
    result = user_dao.get(db, created_user.id)
    
    # Verify it returns a UserResponse (Pydantic object)
    assert isinstance(result, UserResponse)
    assert result.username == "testuser2"
    assert result.email == "test2@example.com"
    assert result.id == created_user.id


def test_user_dao_get_multi_returns_pydantic_objects(db, user_dao):
    """Test that UserDAO.get_multi returns a list of UserResponse objects."""
    # Create multiple users
    for i in range(3):
        user_create = UserCreate(
            username=f"user{i}",
            email=f"user{i}@example.com",
            full_name=f"User {i}"
        )
        user_dao.create(db, obj_in=user_create)
    
    # Get all users
    result = user_dao.get_multi(db, skip=0, limit=10)
    
    # Verify it returns a list of UserResponse objects
    assert isinstance(result, list)
    assert len(result) == 3
    for user in result:
        assert isinstance(user, UserResponse)


def test_user_dao_update_returns_pydantic_object(db, user_dao):
    """Test that UserDAO.update returns a UserResponse (Pydantic object)."""
    # Create a user first
    user_create = UserCreate(
        username="updateuser",
        email="update@example.com",
        full_name="Update User"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Update the user
    user_update = UserUpdate(full_name="Updated User")
    result = user_dao.update_by_id(db, created_user.id, user_update)
    
    # Verify it returns a UserResponse (Pydantic object)
    assert isinstance(result, UserResponse)
    assert result.full_name == "Updated User"
    assert result.username == "updateuser"  # Unchanged
    assert result.id == created_user.id


def test_user_dao_get_by_email_returns_pydantic_object(db, user_dao):
    """Test that UserDAO.get_by_email returns a UserResponse (Pydantic object)."""
    # Create a user first
    user_create = UserCreate(
        username="emailuser",
        email="email@example.com",
        full_name="Email User"
    )
    user_dao.create(db, obj_in=user_create)
    
    # Get user by email
    result = user_dao.get_by_email(db, "email@example.com")
    
    # Verify it returns a UserResponse (Pydantic object)
    assert isinstance(result, UserResponse)
    assert result.email == "email@example.com"
    assert result.username == "emailuser"


def test_first_user_becomes_admin(db, user_dao):
    """Test that the first user created becomes an admin."""
    user_create = UserCreate(
        username="firstuser",
        email="first@example.com",
        full_name="First User"
    )
    
    result = user_dao.create(db, obj_in=user_create)
    
    # First user should be admin
    assert result.role == UserRole.ADMIN


def test_second_user_is_regular_user(db, user_dao):
    """Test that subsequent users are regular users."""
    # Create first user (admin)
    first_user = UserCreate(
        username="firstuser",
        email="first@example.com",
        full_name="First User"
    )
    user_dao.create(db, obj_in=first_user)
    
    # Create second user
    second_user = UserCreate(
        username="seconduser",
        email="second@example.com",
        full_name="Second User"
    )
    result = user_dao.create(db, obj_in=second_user)
    
    # Second user should be regular user
    assert result.role == UserRole.USER
