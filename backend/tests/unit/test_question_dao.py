"""
Unit tests for QuestionDAO to verify proper database operations and Pydantic object returns.
"""
import pytest
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse
from app.schemas.user import UserCreate
from app.models.interview import Question, QuestionImportance, QuestionCategory


def test_question_dao_create_returns_pydantic_object(db, question_dao, user_dao):
    """Test that QuestionDAO.create returns a QuestionResponse (Pydantic object)."""
    # Create a user first (needed for created_by_user_id)
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create a question
    question_create = QuestionCreate(
        title="Criminal Background Check",
        question_text="Have you ever been convicted of a crime?",
        instructions="Please answer honestly and provide details if applicable.",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.CRIMINAL_BACKGROUND,
        created_by_user_id=created_user.id
    )
    
    result = question_dao.create(db, obj_in=question_create)
    
    # Verify it returns a QuestionResponse (Pydantic object)
    assert isinstance(result, QuestionResponse)
    assert result.title == "Criminal Background Check"
    assert result.question_text == "Have you ever been convicted of a crime?"
    assert result.instructions == "Please answer honestly and provide details if applicable."
    assert result.importance == QuestionImportance.MANDATORY
    assert result.category == QuestionCategory.CRIMINAL_BACKGROUND
    assert result.created_by_user_id == created_user.id
    assert result.id is not None
    assert result.created_at is not None
    assert result.updated_at is not None


def test_question_dao_create_without_instructions(db, question_dao, user_dao):
    """Test creating a question without instructions."""
    # Create a user first
    user_create = UserCreate(
        username="testuser2",
        email="test2@example.com",
        full_name="Test User 2"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create a question without instructions
    question_create = QuestionCreate(
        title="Drug Use Question",
        question_text="Have you used illegal drugs in the past year?",
        importance=QuestionImportance.ASK_ONCE,
        category=QuestionCategory.DRUG_USE,
        created_by_user_id=created_user.id
    )

    result = question_dao.create(db, obj_in=question_create)

    assert isinstance(result, QuestionResponse)
    assert result.title == "Drug Use Question"
    assert result.question_text == "Have you used illegal drugs in the past year?"
    assert result.instructions is None
    assert result.importance == QuestionImportance.ASK_ONCE
    assert result.category == QuestionCategory.DRUG_USE
    assert result.id is not None


def test_question_dao_get_returns_pydantic_object(db, question_dao, user_dao):
    """Test that QuestionDAO.get returns a QuestionResponse (Pydantic object)."""
    # Create a user and question first
    user_create = UserCreate(
        username="testuser3",
        email="test3@example.com",
        full_name="Test User 3"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    question_create = QuestionCreate(
        title="Dismissal History",
        question_text="Have you ever been dismissed from a job?",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.DISMISSALS,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)

    # Get the question by ID
    result = question_dao.get(db, created_question.id)

    # Verify it returns a QuestionResponse (Pydantic object)
    assert isinstance(result, QuestionResponse)
    assert result.title == "Dismissal History"
    assert result.question_text == "Have you ever been dismissed from a job?"
    assert result.importance == QuestionImportance.MANDATORY
    assert result.category == QuestionCategory.DISMISSALS
    assert result.id == created_question.id


def test_question_dao_get_nonexistent_returns_none(db, question_dao):
    """Test that getting a non-existent question returns None."""
    result = question_dao.get(db, 99999)
    assert result is None


def test_question_dao_get_multi_returns_pydantic_objects(db, question_dao, user_dao):
    """Test that QuestionDAO.get_multi returns a list of QuestionResponse objects."""
    # Create a user first
    user_create = UserCreate(
        username="testuser4",
        email="test4@example.com",
        full_name="Test User 4"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create multiple questions
    questions_data = [
        {
            "title": "Ethics Question 1",
            "question_text": "Describe a time when you faced an ethical dilemma.",
            "importance": QuestionImportance.MANDATORY,
            "category": QuestionCategory.ETHICS
        },
        {
            "title": "Ethics Question 2",
            "question_text": "How do you handle conflicts of interest?",
            "importance": QuestionImportance.ASK_ONCE,
            "category": QuestionCategory.ETHICS
        },
        {
            "title": "Criminal Question",
            "question_text": "Any criminal history?",
            "importance": QuestionImportance.MANDATORY,
            "category": QuestionCategory.CRIMINAL_BACKGROUND
        }
    ]
    
    for question_data in questions_data:
        question_create = QuestionCreate(
            **question_data,
            created_by_user_id=created_user.id
        )
        question_dao.create(db, obj_in=question_create)
    
    # Get all questions
    result = question_dao.get_multi(db, skip=0, limit=10)
    
    # Verify it returns a list of QuestionResponse objects
    assert isinstance(result, list)
    assert len(result) == 3
    for question in result:
        assert isinstance(question, QuestionResponse)
        assert question.id is not None
        assert question.title is not None
        assert question.created_by_user_id == created_user.id


def test_question_dao_get_multi_with_pagination(db, question_dao, user_dao):
    """Test pagination in get_multi method."""
    # Create a user first
    user_create = UserCreate(
        username="testuser5",
        email="test5@example.com",
        full_name="Test User 5"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create 5 questions
    for i in range(5):
        question_create = QuestionCreate(
            title=f"Question {i}",
            question_text=f"Question text {i}",
            importance=QuestionImportance.OPTIONAL,
            category=QuestionCategory.ETHICS,
            created_by_user_id=created_user.id
        )
        question_dao.create(db, obj_in=question_create)
    
    # Test pagination
    first_page = question_dao.get_multi(db, skip=0, limit=2)
    second_page = question_dao.get_multi(db, skip=2, limit=2)
    
    assert len(first_page) == 2
    assert len(second_page) == 2
    
    # Ensure different questions on different pages
    first_page_ids = {question.id for question in first_page}
    second_page_ids = {question.id for question in second_page}
    assert first_page_ids.isdisjoint(second_page_ids)


def test_question_dao_update_returns_pydantic_object(db, question_dao, user_dao):
    """Test that QuestionDAO.update returns a QuestionResponse (Pydantic object)."""
    # Create a user and question first
    user_create = UserCreate(
        username="testuser6",
        email="test6@example.com",
        full_name="Test User 6"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    question_create = QuestionCreate(
        title="Original Title",
        question_text="Original question text",
        importance=QuestionImportance.OPTIONAL,
        category=QuestionCategory.ETHICS,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)

    # Get the SQLAlchemy model for update
    db_question = db.query(Question).filter(Question.id == created_question.id).first()

    # Update the question
    question_update = QuestionUpdate(
        title="Updated Title",
        importance=QuestionImportance.MANDATORY,
        instructions="New instructions"
    )
    result = question_dao.update(db, db_obj=db_question, obj_in=question_update)

    # Verify it returns a QuestionResponse (Pydantic object)
    assert isinstance(result, QuestionResponse)
    assert result.title == "Updated Title"
    assert result.question_text == "Original question text"  # Unchanged
    assert result.importance == QuestionImportance.MANDATORY
    assert result.instructions == "New instructions"
    assert result.category == QuestionCategory.ETHICS  # Unchanged
    assert result.id == created_question.id


def test_question_dao_update_partial_fields(db, question_dao, user_dao):
    """Test updating only specific fields."""
    # Create a user and question
    user_create = UserCreate(
        username="testuser7",
        email="test7@example.com",
        full_name="Test User 7"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    question_create = QuestionCreate(
        title="Test Question",
        question_text="Test question text",
        importance=QuestionImportance.ASK_ONCE,
        category=QuestionCategory.DRUG_USE,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)

    # Get the SQLAlchemy model for update
    db_question = db.query(Question).filter(Question.id == created_question.id).first()

    # Update only the question text
    question_update = QuestionUpdate(question_text="Updated question text only")
    result = question_dao.update(db, db_obj=db_question, obj_in=question_update)

    # Verify only question text was updated
    assert result.title == "Test Question"  # Unchanged
    assert result.question_text == "Updated question text only"  # Updated
    assert result.importance == QuestionImportance.ASK_ONCE  # Unchanged
    assert result.category == QuestionCategory.DRUG_USE  # Unchanged


def test_question_dao_delete_existing_question(db, question_dao, user_dao):
    """Test deleting an existing question."""
    # Create a user and question
    user_create = UserCreate(
        username="testuser8",
        email="test8@example.com",
        full_name="Test User 8"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    question_create = QuestionCreate(
        title="Question to Delete",
        question_text="This question will be deleted",
        importance=QuestionImportance.OPTIONAL,
        category=QuestionCategory.ETHICS,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)
    
    # Delete the question
    result = question_dao.delete(db, id=created_question.id)
    
    # Verify deletion was successful
    assert result is True
    
    # Verify question no longer exists
    deleted_question = question_dao.get(db, created_question.id)
    assert deleted_question is None


def test_question_dao_delete_nonexistent_question(db, question_dao):
    """Test deleting a non-existent question."""
    result = question_dao.delete(db, id=99999)
    assert result is False


def test_question_dao_get_by_category_returns_pydantic_objects(db, question_dao, user_dao):
    """Test that QuestionDAO.get_by_category returns QuestionResponse objects."""
    # Create a user first
    user_create = UserCreate(
        username="testuser9",
        email="test9@example.com",
        full_name="Test User 9"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create questions in different categories
    questions_data = [
        {
            "title": "Ethics 1",
            "question_text": "Ethics question 1",
            "category": QuestionCategory.ETHICS,
            "importance": QuestionImportance.MANDATORY
        },
        {
            "title": "Ethics 2",
            "question_text": "Ethics question 2",
            "category": QuestionCategory.ETHICS,
            "importance": QuestionImportance.ASK_ONCE
        },
        {
            "title": "Criminal",
            "question_text": "Criminal question",
            "category": QuestionCategory.CRIMINAL_BACKGROUND,
            "importance": QuestionImportance.MANDATORY
        }
    ]
    
    for question_data in questions_data:
        question_create = QuestionCreate(
            **question_data,
            created_by_user_id=created_user.id
        )
        question_dao.create(db, obj_in=question_create)
    
    # Get questions by category
    result = question_dao.get_by_category(db, QuestionCategory.ETHICS)
    
    # Verify it returns QuestionResponse objects
    assert isinstance(result, list)
    assert len(result) == 2  # Two ethics questions
    for question in result:
        assert isinstance(question, QuestionResponse)
        assert question.category == QuestionCategory.ETHICS


def test_question_dao_get_by_importance_returns_pydantic_objects(db, question_dao, user_dao):
    """Test that QuestionDAO.get_by_importance returns QuestionResponse objects."""
    # Create a user first
    user_create = UserCreate(
        username="testuser10",
        email="test10@example.com",
        full_name="Test User 10"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create questions with different importance levels
    questions_data = [
        {
            "title": "Mandatory 1",
            "question_text": "Mandatory importance 1",
            "importance": QuestionImportance.MANDATORY,
            "category": QuestionCategory.ETHICS
        },
        {
            "title": "Mandatory 2",
            "question_text": "Mandatory importance 2",
            "importance": QuestionImportance.MANDATORY,
            "category": QuestionCategory.CRIMINAL_BACKGROUND
        },
        {
            "title": "Ask Once",
            "question_text": "Ask once importance",
            "importance": QuestionImportance.ASK_ONCE,
            "category": QuestionCategory.DRUG_USE
        }
    ]
    
    for question_data in questions_data:
        question_create = QuestionCreate(
            **question_data,
            created_by_user_id=created_user.id
        )
        question_dao.create(db, obj_in=question_create)
    
    # Get questions by importance
    result = question_dao.get_by_importance(db, QuestionImportance.MANDATORY)

    # Verify it returns QuestionResponse objects
    assert isinstance(result, list)
    assert len(result) == 2  # Two mandatory importance questions
    for question in result:
        assert isinstance(question, QuestionResponse)
        assert question.importance == QuestionImportance.MANDATORY
