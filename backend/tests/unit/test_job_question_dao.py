"""
Unit tests for JobQuestionDAO to verify proper database operations and Pydantic object returns.
"""
import pytest
from app.schemas.job_question import JobQuestionCreate, JobQuestionUpdate, JobQuestionResponse
from app.schemas.job import JobCreate
from app.schemas.question import QuestionCreate
from app.schemas.user import UserCreate
from app.models.interview import JobQuestion, QuestionImportance, QuestionCategory


def test_job_question_dao_create_returns_pydantic_object(db, job_question_dao, job_dao, question_dao, user_dao):
    """Test that JobQuestionDAO.create returns a JobQuestionResponse (Pydantic object)."""
    # Create dependencies first
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Software Engineer",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    question_create = QuestionCreate(
        title="Criminal Background",
        question_text="Have you ever been convicted of a crime?",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.CRIMINAL_BACKGROUND,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)
    
    # Create a job question
    job_question_create = JobQuestionCreate(
        job_id=created_job.id,
        question_id=created_question.id,
        order_index=1
    )
    
    result = job_question_dao.create(db, obj_in=job_question_create)
    
    # Verify it returns a JobQuestionResponse (Pydantic object)
    assert isinstance(result, JobQuestionResponse)
    assert result.job_id == created_job.id
    assert result.question_id == created_question.id
    assert result.order_index == 1
    assert result.id is not None


def test_job_question_dao_get_returns_pydantic_object(db, job_question_dao, job_dao, question_dao, user_dao):
    """Test that JobQuestionDAO.get returns a JobQuestionResponse (Pydantic object)."""
    # Create dependencies and job question
    user_create = UserCreate(
        username="testuser2",
        email="test2@example.com",
        full_name="Test User 2"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Data Analyst",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    question_create = QuestionCreate(
        title="Drug Use",
        question_text="Have you used illegal drugs?",
        importance=QuestionImportance.ASK_ONCE,
        category=QuestionCategory.DRUG_USE,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)
    
    job_question_create = JobQuestionCreate(
        job_id=created_job.id,
        question_id=created_question.id,
        order_index=2
    )
    created_job_question = job_question_dao.create(db, obj_in=job_question_create)
    
    # Get the job question by ID
    result = job_question_dao.get(db, created_job_question.id)
    
    # Verify it returns a JobQuestionResponse (Pydantic object)
    assert isinstance(result, JobQuestionResponse)
    assert result.job_id == created_job.id
    assert result.question_id == created_question.id
    assert result.order_index == 2
    assert result.id == created_job_question.id


def test_job_question_dao_get_nonexistent_returns_none(db, job_question_dao):
    """Test that getting a non-existent job question returns None."""
    result = job_question_dao.get(db, 99999)
    assert result is None


def test_job_question_dao_get_multi_returns_pydantic_objects(db, job_question_dao, job_dao, question_dao, user_dao):
    """Test that JobQuestionDAO.get_multi returns a list of JobQuestionResponse objects."""
    # Create dependencies
    user_create = UserCreate(
        username="testuser3",
        email="test3@example.com",
        full_name="Test User 3"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Product Manager",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Create multiple questions
    questions = []
    for i in range(3):
        question_create = QuestionCreate(
            title=f"Question {i}",
            question_text=f"Question text {i}",
            importance=QuestionImportance.ASK_ONCE,
            category=QuestionCategory.ETHICS,
            created_by_user_id=created_user.id
        )
        questions.append(question_dao.create(db, obj_in=question_create))
    
    # Create multiple job questions
    for i, question in enumerate(questions):
        job_question_create = JobQuestionCreate(
            job_id=created_job.id,
            question_id=question.id,
            order_index=i + 1
        )
        job_question_dao.create(db, obj_in=job_question_create)
    
    # Get all job questions
    result = job_question_dao.get_multi(db, skip=0, limit=10)
    
    # Verify it returns a list of JobQuestionResponse objects
    assert isinstance(result, list)
    assert len(result) == 3
    for job_question in result:
        assert isinstance(job_question, JobQuestionResponse)
        assert job_question.id is not None
        assert job_question.job_id == created_job.id


def test_job_question_dao_get_multi_with_pagination(db, job_question_dao, job_dao, question_dao, user_dao):
    """Test pagination in get_multi method."""
    # Create dependencies
    user_create = UserCreate(
        username="testuser4",
        email="test4@example.com",
        full_name="Test User 4"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Test Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Create 5 job questions
    for i in range(5):
        question_create = QuestionCreate(
            title=f"Question {i}",
            question_text=f"Question text {i}",
            importance=QuestionImportance.OPTIONAL,
            category=QuestionCategory.ETHICS,
            created_by_user_id=created_user.id
        )
        created_question = question_dao.create(db, obj_in=question_create)
        
        job_question_create = JobQuestionCreate(
            job_id=created_job.id,
            question_id=created_question.id,
            order_index=i + 1
        )
        job_question_dao.create(db, obj_in=job_question_create)
    
    # Test pagination
    first_page = job_question_dao.get_multi(db, skip=0, limit=2)
    second_page = job_question_dao.get_multi(db, skip=2, limit=2)
    
    assert len(first_page) == 2
    assert len(second_page) == 2
    
    # Ensure different job questions on different pages
    first_page_ids = {jq.id for jq in first_page}
    second_page_ids = {jq.id for jq in second_page}
    assert first_page_ids.isdisjoint(second_page_ids)


def test_job_question_dao_update_returns_pydantic_object(db, job_question_dao, job_dao, question_dao, user_dao):
    """Test that JobQuestionDAO.update returns a JobQuestionResponse (Pydantic object)."""
    # Create dependencies and job question
    user_create = UserCreate(
        username="testuser5",
        email="test5@example.com",
        full_name="Test User 5"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Update Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    question_create = QuestionCreate(
        title="Update Question",
        question_text="Update question text",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.DISMISSALS,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)
    
    job_question_create = JobQuestionCreate(
        job_id=created_job.id,
        question_id=created_question.id,
        order_index=5
    )
    created_job_question = job_question_dao.create(db, obj_in=job_question_create)
    
    # Get the SQLAlchemy model for update
    db_job_question = db.query(JobQuestion).filter(JobQuestion.id == created_job_question.id).first()
    
    # Update the job question
    job_question_update = JobQuestionUpdate(order_index=10)
    result = job_question_dao.update(db, db_obj=db_job_question, obj_in=job_question_update)
    
    # Verify it returns a JobQuestionResponse (Pydantic object)
    assert isinstance(result, JobQuestionResponse)
    assert result.order_index == 10
    assert result.job_id == created_job.id  # Unchanged
    assert result.question_id == created_question.id  # Unchanged
    assert result.id == created_job_question.id


def test_job_question_dao_delete_existing_job_question(db, job_question_dao, job_dao, question_dao, user_dao):
    """Test deleting an existing job question."""
    # Create dependencies and job question
    user_create = UserCreate(
        username="testuser6",
        email="test6@example.com",
        full_name="Test User 6"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Delete Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    question_create = QuestionCreate(
        title="Delete Question",
        question_text="Delete question text",
        importance=QuestionImportance.OPTIONAL,
        category=QuestionCategory.ETHICS,
        created_by_user_id=created_user.id
    )
    created_question = question_dao.create(db, obj_in=question_create)
    
    job_question_create = JobQuestionCreate(
        job_id=created_job.id,
        question_id=created_question.id,
        order_index=1
    )
    created_job_question = job_question_dao.create(db, obj_in=job_question_create)
    
    # Delete the job question
    result = job_question_dao.delete(db, id=created_job_question.id)
    
    # Verify deletion was successful
    assert result is True
    
    # Verify job question no longer exists
    deleted_job_question = job_question_dao.get(db, created_job_question.id)
    assert deleted_job_question is None


def test_job_question_dao_delete_nonexistent_job_question(db, job_question_dao):
    """Test deleting a non-existent job question."""
    result = job_question_dao.delete(db, id=99999)
    assert result is False


def test_job_question_dao_get_by_job_returns_pydantic_objects(db, job_question_dao, job_dao, question_dao, user_dao):
    """Test that JobQuestionDAO.get_by_job returns JobQuestionResponse objects ordered by order_index."""
    # Create dependencies
    user_create = UserCreate(
        username="testuser7",
        email="test7@example.com",
        full_name="Test User 7"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create two jobs
    job1_create = JobCreate(
        title="Job 1",
        created_by_user_id=created_user.id
    )
    job2_create = JobCreate(
        title="Job 2",
        created_by_user_id=created_user.id
    )
    job1 = job_dao.create(db, obj_in=job1_create)
    job2 = job_dao.create(db, obj_in=job2_create)
    
    # Create questions
    questions = []
    for i in range(3):
        question_create = QuestionCreate(
            title=f"Question {i}",
            question_text=f"Question text {i}",
            importance=QuestionImportance.ASK_ONCE,
            category=QuestionCategory.ETHICS,
            created_by_user_id=created_user.id
        )
        questions.append(question_dao.create(db, obj_in=question_create))
    
    # Create job questions for job1 with specific order
    order_indices = [3, 1, 2]  # Intentionally out of order
    for i, question in enumerate(questions):
        job_question_create = JobQuestionCreate(
            job_id=job1.id,
            question_id=question.id,
            order_index=order_indices[i]
        )
        job_question_dao.create(db, obj_in=job_question_create)
    
    # Create one job question for job2
    job_question_create = JobQuestionCreate(
        job_id=job2.id,
        question_id=questions[0].id,
        order_index=1
    )
    job_question_dao.create(db, obj_in=job_question_create)
    
    # Get job questions for job1
    result = job_question_dao.get_by_job(db, job1.id)
    
    # Verify it returns JobQuestionResponse objects ordered by order_index
    assert isinstance(result, list)
    assert len(result) == 3  # Only job1's questions
    for job_question in result:
        assert isinstance(job_question, JobQuestionResponse)
        assert job_question.job_id == job1.id
    
    # Verify order
    assert result[0].order_index == 1
    assert result[1].order_index == 2
    assert result[2].order_index == 3


def test_job_question_dao_get_by_question_returns_pydantic_objects(db, job_question_dao, job_dao, question_dao, user_dao):
    """Test that JobQuestionDAO.get_by_question returns JobQuestionResponse objects."""
    # Create dependencies
    user_create = UserCreate(
        username="testuser8",
        email="test8@example.com",
        full_name="Test User 8"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create jobs
    jobs = []
    for i in range(2):
        job_create = JobCreate(
            title=f"Job {i}",
            created_by_user_id=created_user.id
        )
        jobs.append(job_dao.create(db, obj_in=job_create))
    
    # Create questions
    question1_create = QuestionCreate(
        title="Popular Question",
        question_text="This question is used in multiple jobs",
        importance=QuestionImportance.MANDATORY,
        category=QuestionCategory.CRIMINAL_BACKGROUND,
        created_by_user_id=created_user.id
    )
    question2_create = QuestionCreate(
        title="Unique Question",
        question_text="This question is used in one job only",
        importance=QuestionImportance.ASK_ONCE,
        category=QuestionCategory.ETHICS,
        created_by_user_id=created_user.id
    )
    question1 = question_dao.create(db, obj_in=question1_create)
    question2 = question_dao.create(db, obj_in=question2_create)
    
    # Create job questions - question1 used in both jobs, question2 in one job
    for job in jobs:
        job_question_create = JobQuestionCreate(
            job_id=job.id,
            question_id=question1.id,
            order_index=1
        )
        job_question_dao.create(db, obj_in=job_question_create)
    
    job_question_create = JobQuestionCreate(
        job_id=jobs[0].id,
        question_id=question2.id,
        order_index=2
    )
    job_question_dao.create(db, obj_in=job_question_create)
    
    # Get job questions for question1 (should be in 2 jobs)
    result1 = job_question_dao.get_by_question(db, question1.id)
    
    # Get job questions for question2 (should be in 1 job)
    result2 = job_question_dao.get_by_question(db, question2.id)
    
    # Verify results
    assert isinstance(result1, list)
    assert len(result1) == 2  # question1 used in 2 jobs
    for job_question in result1:
        assert isinstance(job_question, JobQuestionResponse)
        assert job_question.question_id == question1.id
    
    assert isinstance(result2, list)
    assert len(result2) == 1  # question2 used in 1 job
    assert result2[0].question_id == question2.id


def test_job_question_dao_bulk_create_for_job(db, job_question_dao, job_dao, question_dao, user_dao):
    """Test bulk creation of job questions for a job."""
    # Create dependencies
    user_create = UserCreate(
        username="testuser9",
        email="test9@example.com",
        full_name="Test User 9"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Bulk Job",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Create multiple questions
    question_ids = []
    for i in range(4):
        question_create = QuestionCreate(
            title=f"Bulk Question {i}",
            question_text=f"Bulk question text {i}",
            importance=QuestionImportance.ASK_ONCE,
            category=QuestionCategory.ETHICS,
            created_by_user_id=created_user.id
        )
        question = question_dao.create(db, obj_in=question_create)
        question_ids.append(question.id)
    
    # Bulk create job questions
    result = job_question_dao.bulk_create_for_job(db, created_job.id, question_ids)
    
    # Verify results
    assert isinstance(result, list)
    assert len(result) == 4
    
    for i, job_question in enumerate(result):
        assert isinstance(job_question, JobQuestionResponse)
        assert job_question.job_id == created_job.id
        assert job_question.question_id == question_ids[i]
        assert job_question.order_index == i + 1  # Should be ordered 1, 2, 3, 4
