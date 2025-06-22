"""
Unit tests for UserService to verify proper dependency injection and business logic.
"""
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import UserRole
from app.services.user_service import UserService


def test_user_service_dependency_injection(user_dao):
    """Test that UserService properly accepts UserDAO dependency."""
    service = UserService(user_dao)
    assert service.user_dao is user_dao


def test_user_service_create_user_returns_pydantic(db, user_service):
    """Test that UserService.create_user returns UserResponse."""
    user_create = UserCreate(
        username="serviceuser",
        email="service@example.com",
        full_name="Service User"
    )
    
    result = user_service.create_user(db, user_create)
    
    assert isinstance(result, UserResponse)
    assert result.username == "serviceuser"
    assert result.email == "service@example.com"


def test_user_service_get_user_by_id_returns_pydantic(db, user_service):
    """Test that UserService.get_user_by_id returns UserResponse."""
    # Create user first
    user_create = UserCreate(
        username="getuser",
        email="get@example.com",
        full_name="Get User"
    )
    created_user = user_service.create_user(db, user_create)
    
    # Get user by ID
    result = user_service.get_user_by_id(db, created_user.id)
    
    assert isinstance(result, UserResponse)
    assert result.id == created_user.id
    assert result.username == "getuser"


def test_user_service_get_users_returns_pydantic_list(db, user_service):
    """Test that UserService.get_users returns list of UserResponse."""
    # Create multiple users
    for i in range(2):
        user_create = UserCreate(
            username=f"listuser{i}",
            email=f"list{i}@example.com",
            full_name=f"List User {i}"
        )
        user_service.create_user(db, user_create)
    
    # Get users
    result = user_service.get_users(db, skip=0, limit=10)
    
    assert isinstance(result, list)
    assert len(result) == 2
    for user in result:
        assert isinstance(user, UserResponse)


def test_user_service_create_user_from_params(db, user_service):
    """Test UserService.create_user_from_params legacy method."""
    result = user_service.create_user_from_params(
        db=db,
        username="paramuser",
        email="param@example.com",
        full_name="Param User",
        role=UserRole.USER
    )
    
    assert isinstance(result, UserResponse)
    assert result.username == "paramuser"
    assert result.email == "param@example.com"
    assert result.role == UserRole.ADMIN  # First user becomes admin


def test_user_service_update_user_returns_pydantic(db, user_service):
    """Test that UserService.update_user returns UserResponse."""
    # Create user first
    user_create = UserCreate(
        username="updateuser",
        email="update@example.com",
        full_name="Update User"
    )
    created_user = user_service.create_user(db, user_create)
    
    # Update user
    user_update = UserUpdate(full_name="Updated User")
    result = user_service.update_user(db, created_user.id, user_update)
    
    assert isinstance(result, UserResponse)
    assert result.full_name == "Updated User"
    assert result.id == created_user.id


def test_user_service_get_user_by_email_returns_pydantic(db, user_service):
    """Test that UserService.get_user_by_email returns UserResponse."""
    # Create user first
    user_create = UserCreate(
        username="emailuser",
        email="email@example.com",
        full_name="Email User"
    )
    user_service.create_user(db, user_create)
    
    # Get user by email
    result = user_service.get_user_by_email(db, "email@example.com")
    
    assert isinstance(result, UserResponse)
    assert result.email == "email@example.com"


def test_user_service_get_user_by_username_returns_pydantic(db, user_service):
    """Test that UserService.get_user_by_username returns UserResponse."""
    # Create user first
    user_create = UserCreate(
        username="usernameuser",
        email="username@example.com",
        full_name="Username User"
    )
    user_service.create_user(db, user_create)
    
    # Get user by username
    result = user_service.get_user_by_username(db, "usernameuser")
    
    assert isinstance(result, UserResponse)
    assert result.username == "usernameuser"


def test_user_service_delete_user(db, user_service):
    """Test that UserService.delete_user works correctly."""
    # Create user first
    user_create = UserCreate(
        username="deleteuser",
        email="delete@example.com",
        full_name="Delete User"
    )
    created_user = user_service.create_user(db, user_create)
    
    # Delete user
    result = user_service.delete_user(db, created_user.id)
    
    assert result is True
    
    # Verify user is deleted
    deleted_user = user_service.get_user_by_id(db, created_user.id)
    assert deleted_user is None


def test_user_service_get_user_count(db, user_service):
    """Test that UserService.get_user_count returns correct count."""
    # Initially no users
    assert user_service.get_user_count(db) == 0
    
    # Create a user
    user_create = UserCreate(
        username="countuser",
        email="count@example.com",
        full_name="Count User"
    )
    user_service.create_user(db, user_create)
    
    # Should have 1 user
    assert user_service.get_user_count(db) == 1


def test_user_service_is_first_user(db, user_service):
    """Test that UserService.is_first_user works correctly."""
    # Initially should be first user
    assert user_service.is_first_user(db) is True
    
    # Create a user
    user_create = UserCreate(
        username="firstuser",
        email="first@example.com",
        full_name="First User"
    )
    user_service.create_user(db, user_create)
    
    # Should no longer be first user
    assert user_service.is_first_user(db) is False
