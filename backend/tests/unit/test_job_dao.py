"""
Unit tests for JobDAO to verify proper database operations and Pydantic object returns.
"""
import pytest
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.schemas.user import UserCreate
from app.models.interview import Job


def test_job_dao_create_returns_pydantic_object(db, job_dao, user_dao):
    """Test that JobDAO.create returns a JobResponse (Pydantic object)."""
    # Create a user first (needed for created_by_user_id)
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create a job
    job_create = JobCreate(
        title="Software Engineer",
        description="Develop and maintain software applications",
        department="Engineering",
        created_by_user_id=created_user.id
    )
    
    result = job_dao.create(db, obj_in=job_create)
    
    # Verify it returns a JobResponse (Pydantic object)
    assert isinstance(result, JobResponse)
    assert result.title == "Software Engineer"
    assert result.description == "Develop and maintain software applications"
    assert result.department == "Engineering"
    assert result.created_by_user_id == created_user.id
    assert result.id is not None
    assert result.created_at is not None
    assert result.updated_at is not None


def test_job_dao_create_without_optional_fields(db, job_dao, user_dao):
    """Test creating a job without optional fields."""
    # Create a user first
    user_create = UserCreate(
        username="testuser2",
        email="test2@example.com",
        full_name="Test User 2"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create a job with minimal data
    job_create = JobCreate(
        title="Data Analyst",
        created_by_user_id=created_user.id
    )
    
    result = job_dao.create(db, obj_in=job_create)
    
    assert isinstance(result, JobResponse)
    assert result.title == "Data Analyst"
    assert result.description is None
    assert result.department is None
    assert result.created_by_user_id == created_user.id
    assert result.id is not None


def test_job_dao_get_returns_pydantic_object(db, job_dao, user_dao):
    """Test that JobDAO.get returns a JobResponse (Pydantic object)."""
    # Create a user and job first
    user_create = UserCreate(
        username="testuser3",
        email="test3@example.com",
        full_name="Test User 3"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Product Manager",
        description="Manage product development lifecycle",
        department="Product",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Get the job by ID
    result = job_dao.get(db, created_job.id)
    
    # Verify it returns a JobResponse (Pydantic object)
    assert isinstance(result, JobResponse)
    assert result.title == "Product Manager"
    assert result.description == "Manage product development lifecycle"
    assert result.department == "Product"
    assert result.id == created_job.id


def test_job_dao_get_nonexistent_returns_none(db, job_dao):
    """Test that getting a non-existent job returns None."""
    result = job_dao.get(db, 99999)
    assert result is None


def test_job_dao_get_multi_returns_pydantic_objects(db, job_dao, user_dao):
    """Test that JobDAO.get_multi returns a list of JobResponse objects."""
    # Create a user first
    user_create = UserCreate(
        username="testuser4",
        email="test4@example.com",
        full_name="Test User 4"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create multiple jobs
    jobs_data = [
        {"title": "Frontend Developer", "department": "Engineering"},
        {"title": "Backend Developer", "department": "Engineering"},
        {"title": "DevOps Engineer", "department": "Infrastructure"}
    ]
    
    for job_data in jobs_data:
        job_create = JobCreate(
            **job_data,
            created_by_user_id=created_user.id
        )
        job_dao.create(db, obj_in=job_create)
    
    # Get all jobs
    result = job_dao.get_multi(db, skip=0, limit=10)
    
    # Verify it returns a list of JobResponse objects
    assert isinstance(result, list)
    assert len(result) == 3
    for job in result:
        assert isinstance(job, JobResponse)
        assert job.id is not None
        assert job.title is not None
        assert job.created_by_user_id == created_user.id


def test_job_dao_get_multi_with_pagination(db, job_dao, user_dao):
    """Test pagination in get_multi method."""
    # Create a user first
    user_create = UserCreate(
        username="testuser5",
        email="test5@example.com",
        full_name="Test User 5"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create 5 jobs
    for i in range(5):
        job_create = JobCreate(
            title=f"Job {i}",
            department=f"Department {i}",
            created_by_user_id=created_user.id
        )
        job_dao.create(db, obj_in=job_create)
    
    # Test pagination
    first_page = job_dao.get_multi(db, skip=0, limit=2)
    second_page = job_dao.get_multi(db, skip=2, limit=2)
    
    assert len(first_page) == 2
    assert len(second_page) == 2
    
    # Ensure different jobs on different pages
    first_page_ids = {job.id for job in first_page}
    second_page_ids = {job.id for job in second_page}
    assert first_page_ids.isdisjoint(second_page_ids)


def test_job_dao_update_returns_pydantic_object(db, job_dao, user_dao):
    """Test that JobDAO.update returns a JobResponse (Pydantic object)."""
    # Create a user and job first
    user_create = UserCreate(
        username="testuser6",
        email="test6@example.com",
        full_name="Test User 6"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Original Title",
        description="Original description",
        department="Original Department",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Get the SQLAlchemy model for update
    db_job = db.query(Job).filter(Job.id == created_job.id).first()
    
    # Update the job
    job_update = JobUpdate(
        title="Updated Title",
        department="Updated Department"
    )
    result = job_dao.update(db, db_obj=db_job, obj_in=job_update)
    
    # Verify it returns a JobResponse (Pydantic object)
    assert isinstance(result, JobResponse)
    assert result.title == "Updated Title"
    assert result.description == "Original description"  # Unchanged
    assert result.department == "Updated Department"
    assert result.id == created_job.id


def test_job_dao_update_partial_fields(db, job_dao, user_dao):
    """Test updating only specific fields."""
    # Create a user and job
    user_create = UserCreate(
        username="testuser7",
        email="test7@example.com",
        full_name="Test User 7"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Test Job",
        description="Test description",
        department="Test Department",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Get the SQLAlchemy model for update
    db_job = db.query(Job).filter(Job.id == created_job.id).first()
    
    # Update only the description
    job_update = JobUpdate(description="Updated description only")
    result = job_dao.update(db, db_obj=db_job, obj_in=job_update)
    
    # Verify only description was updated
    assert result.title == "Test Job"  # Unchanged
    assert result.description == "Updated description only"  # Updated
    assert result.department == "Test Department"  # Unchanged


def test_job_dao_delete_existing_job(db, job_dao, user_dao):
    """Test deleting an existing job."""
    # Create a user and job
    user_create = UserCreate(
        username="testuser8",
        email="test8@example.com",
        full_name="Test User 8"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Job to Delete",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Delete the job
    result = job_dao.delete(db, id=created_job.id)
    
    # Verify deletion was successful
    assert result is True
    
    # Verify job no longer exists
    deleted_job = job_dao.get(db, created_job.id)
    assert deleted_job is None


def test_job_dao_delete_nonexistent_job(db, job_dao):
    """Test deleting a non-existent job."""
    result = job_dao.delete(db, id=99999)
    assert result is False


def test_job_dao_get_by_department_returns_pydantic_objects(db, job_dao, user_dao):
    """Test that JobDAO.get_by_department returns JobResponse objects."""
    # Create a user first
    user_create = UserCreate(
        username="testuser9",
        email="test9@example.com",
        full_name="Test User 9"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create jobs in different departments
    jobs_data = [
        {"title": "Engineer 1", "department": "Engineering"},
        {"title": "Engineer 2", "department": "Engineering"},
        {"title": "Sales Rep", "department": "Sales"}
    ]
    
    for job_data in jobs_data:
        job_create = JobCreate(
            **job_data,
            created_by_user_id=created_user.id
        )
        job_dao.create(db, obj_in=job_create)
    
    # Get jobs by department
    result = job_dao.get_by_department(db, "Engineering")
    
    # Verify it returns JobResponse objects
    assert isinstance(result, list)
    assert len(result) == 2  # Two engineering jobs
    for job in result:
        assert isinstance(job, JobResponse)
        assert job.department == "Engineering"


def test_job_dao_get_by_creator_returns_pydantic_objects(db, job_dao, user_dao):
    """Test that JobDAO.get_by_creator returns JobResponse objects."""
    # Create two users
    user1_create = UserCreate(
        username="user1",
        email="user1@example.com",
        full_name="User 1"
    )
    user2_create = UserCreate(
        username="user2",
        email="user2@example.com",
        full_name="User 2"
    )
    user1 = user_dao.create(db, obj_in=user1_create)
    user2 = user_dao.create(db, obj_in=user2_create)
    
    # Create jobs for different users
    job1_create = JobCreate(
        title="Job by User 1",
        created_by_user_id=user1.id
    )
    job2_create = JobCreate(
        title="Another Job by User 1",
        created_by_user_id=user1.id
    )
    job3_create = JobCreate(
        title="Job by User 2",
        created_by_user_id=user2.id
    )
    
    job_dao.create(db, obj_in=job1_create)
    job_dao.create(db, obj_in=job2_create)
    job_dao.create(db, obj_in=job3_create)
    
    # Get jobs by creator
    result = job_dao.get_by_creator(db, user1.id)
    
    # Verify it returns JobResponse objects for user1 only
    assert isinstance(result, list)
    assert len(result) == 2  # Two jobs by user1
    for job in result:
        assert isinstance(job, JobResponse)
        assert job.created_by_user_id == user1.id
