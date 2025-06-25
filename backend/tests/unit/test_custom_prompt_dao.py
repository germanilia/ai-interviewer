"""
Unit tests for CustomPromptDAO to verify proper database operations and Pydantic object returns.
"""
import pytest
from app.schemas.custom_prompt import CustomPromptCreate, CustomPromptUpdate, CustomPromptResponse
from app.models.custom_prompt import PromptType
from app.crud.user import UserDAO
from app.crud.custom_prompt import CustomPromptDAO
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


@pytest.fixture
def custom_prompt_dao():
    """Create a CustomPromptDAO instance."""
    return CustomPromptDAO()


def test_custom_prompt_dao_create_returns_pydantic_object(db, custom_prompt_dao, test_user_id):
    """Test that CustomPromptDAO.create returns a CustomPromptResponse (Pydantic object)."""
    prompt_create = CustomPromptCreate(
        prompt_type=PromptType.SMALL_LLM,
        name="Test Small LLM Prompt",
        content="You are a test prompt for {candidate_name}",
        description="A test prompt for unit testing",
        is_active=True,
        created_by_user_id=test_user_id
    )
    
    result = custom_prompt_dao.create(db, obj_in=prompt_create, created_by_user_id=test_user_id)
    
    # Verify it returns a CustomPromptResponse (Pydantic object)
    assert isinstance(result, CustomPromptResponse)
    assert result.prompt_type == PromptType.SMALL_LLM
    assert result.name == "Test Small LLM Prompt"
    assert result.content == "You are a test prompt for {candidate_name}"
    assert result.description == "A test prompt for unit testing"
    assert result.is_active is True
    assert result.created_by_user_id == test_user_id
    assert result.id is not None


def test_custom_prompt_dao_get_returns_pydantic_object(db, custom_prompt_dao, test_user_id):
    """Test that CustomPromptDAO.get returns a CustomPromptResponse (Pydantic object)."""
    # Create a prompt first
    prompt_create = CustomPromptCreate(
        prompt_type=PromptType.JUDGE,
        name="Test Judge Prompt",
        content="You are a judge prompt for {candidate_name}",
        description="A test judge prompt",
        is_active=False,
        created_by_user_id=test_user_id
    )
    created_prompt = custom_prompt_dao.create(db, obj_in=prompt_create, created_by_user_id=test_user_id)
    
    # Get the prompt by ID
    result = custom_prompt_dao.get(db, created_prompt.id)
    
    # Verify it returns a CustomPromptResponse (Pydantic object)
    assert isinstance(result, CustomPromptResponse)
    assert result.prompt_type == PromptType.JUDGE
    assert result.name == "Test Judge Prompt"
    assert result.id == created_prompt.id


def test_custom_prompt_dao_get_nonexistent_returns_none(db, custom_prompt_dao):
    """Test that getting a non-existent custom prompt returns None."""
    result = custom_prompt_dao.get(db, 99999)
    assert result is None


def test_custom_prompt_dao_get_multi_returns_pydantic_objects(db, custom_prompt_dao, test_user_id):
    """Test that CustomPromptDAO.get_multi returns a list of CustomPromptResponse objects."""
    # Create multiple prompts
    prompt_types = [PromptType.SMALL_LLM, PromptType.JUDGE, PromptType.GUARDRAILS]
    for i, prompt_type in enumerate(prompt_types):
        prompt_create = CustomPromptCreate(
            prompt_type=prompt_type,
            name=f"Test {prompt_type.value} Prompt {i}",
            content=f"Test content for {prompt_type.value}",
            description=f"Test description {i}",
            is_active=True,
            created_by_user_id=test_user_id
        )
        custom_prompt_dao.create(db, obj_in=prompt_create, created_by_user_id=test_user_id)
    
    # Get all prompts
    result = custom_prompt_dao.get_multi(db, skip=0, limit=10)
    
    # Verify it returns a list of CustomPromptResponse objects
    assert isinstance(result, list)
    assert len(result) == 3
    for prompt in result:
        assert isinstance(prompt, CustomPromptResponse)


def test_custom_prompt_dao_update_returns_pydantic_object(db, custom_prompt_dao, test_user_id):
    """Test that CustomPromptDAO.update returns a CustomPromptResponse (Pydantic object)."""
    # Create a prompt first
    prompt_create = CustomPromptCreate(
        prompt_type=PromptType.GUARDRAILS,
        name="Original Guardrails Prompt",
        content="Original content",
        description="Original description",
        is_active=True,
        created_by_user_id=test_user_id
    )
    created_prompt = custom_prompt_dao.create(db, obj_in=prompt_create, created_by_user_id=test_user_id)
    
    # Get the database object for update
    db_prompt = db.query(custom_prompt_dao.model).filter(custom_prompt_dao.model.id == created_prompt.id).first()
    
    # Update the prompt
    prompt_update = CustomPromptUpdate(
        name="Updated Guardrails Prompt",
        content="Updated content",
        is_active=False
    )
    result = custom_prompt_dao.update(db, db_obj=db_prompt, obj_in=prompt_update)
    
    # Verify it returns a CustomPromptResponse (Pydantic object)
    assert isinstance(result, CustomPromptResponse)
    assert result.name == "Updated Guardrails Prompt"
    assert result.content == "Updated content"
    assert result.is_active is False
    assert result.id == created_prompt.id


def test_custom_prompt_dao_delete_returns_boolean(db, custom_prompt_dao, test_user_id):
    """Test that CustomPromptDAO.delete returns a boolean."""
    # Create a prompt first
    prompt_create = CustomPromptCreate(
        prompt_type=PromptType.SMALL_LLM,
        name="Prompt to Delete",
        content="This prompt will be deleted",
        created_by_user_id=test_user_id
    )
    created_prompt = custom_prompt_dao.create(db, obj_in=prompt_create, created_by_user_id=test_user_id)
    
    # Delete the prompt
    result = custom_prompt_dao.delete(db, id=created_prompt.id)
    
    # Verify it returns True
    assert result is True
    
    # Verify the prompt is actually deleted
    deleted_prompt = custom_prompt_dao.get(db, created_prompt.id)
    assert deleted_prompt is None


def test_custom_prompt_dao_delete_nonexistent_returns_false(db, custom_prompt_dao):
    """Test that deleting a non-existent prompt returns False."""
    result = custom_prompt_dao.delete(db, id=99999)
    assert result is False


def test_custom_prompt_dao_get_by_type(db, custom_prompt_dao, test_user_id):
    """Test CustomPromptDAO.get_by_type method."""
    # Create prompts of different types
    small_llm_prompt = CustomPromptCreate(
        prompt_type=PromptType.SMALL_LLM,
        name="Small LLM Prompt",
        content="Small LLM content",
        is_active=True,
        created_by_user_id=test_user_id
    )
    judge_prompt = CustomPromptCreate(
        prompt_type=PromptType.JUDGE,
        name="Judge Prompt",
        content="Judge content",
        is_active=False,
        created_by_user_id=test_user_id
    )
    
    custom_prompt_dao.create(db, obj_in=small_llm_prompt, created_by_user_id=test_user_id)
    custom_prompt_dao.create(db, obj_in=judge_prompt, created_by_user_id=test_user_id)
    
    # Get only small_llm prompts (active only)
    small_llm_results = custom_prompt_dao.get_by_type(db, PromptType.SMALL_LLM, active_only=True)
    assert len(small_llm_results) == 1
    assert small_llm_results[0].prompt_type == PromptType.SMALL_LLM
    assert small_llm_results[0].is_active is True
    
    # Get judge prompts (including inactive)
    judge_results = custom_prompt_dao.get_by_type(db, PromptType.JUDGE, active_only=False)
    assert len(judge_results) == 1
    assert judge_results[0].prompt_type == PromptType.JUDGE
    assert judge_results[0].is_active is False


def test_custom_prompt_dao_get_active_by_type(db, custom_prompt_dao, test_user_id):
    """Test CustomPromptDAO.get_active_by_type method."""
    # Create multiple prompts of the same type, only one active
    for i in range(3):
        prompt_create = CustomPromptCreate(
            prompt_type=PromptType.SMALL_LLM,
            name=f"Small LLM Prompt {i}",
            content=f"Content {i}",
            is_active=(i == 1),  # Only the second one is active
            created_by_user_id=test_user_id
        )
        custom_prompt_dao.create(db, obj_in=prompt_create, created_by_user_id=test_user_id)
    
    # Get the active prompt
    result = custom_prompt_dao.get_active_by_type(db, PromptType.SMALL_LLM)
    
    assert result is not None
    assert isinstance(result, CustomPromptResponse)
    assert result.name == "Small LLM Prompt 1"
    assert result.is_active is True


def test_custom_prompt_dao_get_active_by_type_none_active(db, custom_prompt_dao, test_user_id):
    """Test CustomPromptDAO.get_active_by_type when no prompts are active."""
    # Create inactive prompt
    prompt_create = CustomPromptCreate(
        prompt_type=PromptType.GUARDRAILS,
        name="Inactive Guardrails Prompt",
        content="Inactive content",
        is_active=False,
        created_by_user_id=test_user_id
    )
    custom_prompt_dao.create(db, obj_in=prompt_create, created_by_user_id=test_user_id)
    
    # Try to get active prompt
    result = custom_prompt_dao.get_active_by_type(db, PromptType.GUARDRAILS)
    assert result is None


def test_custom_prompt_dao_activate_prompt(db, custom_prompt_dao, test_user_id):
    """Test CustomPromptDAO.activate_prompt method."""
    # Create multiple prompts of the same type
    prompt_ids = []
    for i in range(3):
        prompt_create = CustomPromptCreate(
            prompt_type=PromptType.JUDGE,
            name=f"Judge Prompt {i}",
            content=f"Content {i}",
            is_active=(i == 0),  # Only first one is initially active
            created_by_user_id=test_user_id
        )
        created = custom_prompt_dao.create(db, obj_in=prompt_create, created_by_user_id=test_user_id)
        prompt_ids.append(created.id)
    
    # Activate the second prompt (should deactivate others)
    result = custom_prompt_dao.activate_prompt(db, prompt_ids[1], deactivate_others=True)
    
    assert result is not None
    assert result.id == prompt_ids[1]
    assert result.is_active is True
    
    # Verify others are deactivated
    for i, prompt_id in enumerate(prompt_ids):
        prompt = custom_prompt_dao.get(db, prompt_id)
        if i == 1:
            assert prompt.is_active is True
        else:
            assert prompt.is_active is False


def test_custom_prompt_dao_get_count_by_type(db, custom_prompt_dao, test_user_id):
    """Test CustomPromptDAO.get_count_by_type method."""
    # Create prompts of different types
    prompt_data = [
        (PromptType.SMALL_LLM, 2),
        (PromptType.JUDGE, 1),
        (PromptType.GUARDRAILS, 3)
    ]
    
    for prompt_type, count in prompt_data:
        for i in range(count):
            prompt_create = CustomPromptCreate(
                prompt_type=prompt_type,
                name=f"{prompt_type.value} Prompt {i}",
                content=f"Content for {prompt_type.value} {i}",
                created_by_user_id=test_user_id
            )
            custom_prompt_dao.create(db, obj_in=prompt_create, created_by_user_id=test_user_id)
    
    # Get counts
    counts = custom_prompt_dao.get_count_by_type(db)
    
    assert counts[PromptType.SMALL_LLM] == 2
    assert counts[PromptType.JUDGE] == 1
    assert counts[PromptType.GUARDRAILS] == 3
