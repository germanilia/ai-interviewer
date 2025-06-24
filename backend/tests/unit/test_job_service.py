"""
Unit tests for JobService to verify business logic and coordination.
"""
import pytest
from unittest.mock import Mock, MagicMock, ANY
from app.services.job_service import JobService
from app.schemas.job import (
    JobCreate, JobUpdate, JobResponse, JobListResponse, JobFilter,
    JobStatistics, JobCloneRequest, JobWithQuestions
)
from app.schemas.user import UserCreate
from datetime import datetime


@pytest.fixture
def mock_job_dao():
    """Mock JobDAO for testing."""
    return Mock()


@pytest.fixture
def mock_job_question_dao():
    """Mock JobQuestionDAO for testing."""
    return Mock()


@pytest.fixture
def job_service(mock_job_dao, mock_job_question_dao):
    """JobService instance with mocked dependencies."""
    return JobService(
        job_dao=mock_job_dao,
        job_question_dao=mock_job_question_dao
    )


@pytest.fixture
def sample_job_response():
    """Sample JobResponse for testing."""
    return JobResponse(
        id=1,
        title="Software Engineer",
        description="Develop software applications",
        department="Engineering",
        created_by_user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def test_job_service_get_jobs_without_filters(job_service, mock_job_dao, sample_job_response):
    """Test getting jobs without filters."""
    # Setup mock
    mock_job_dao.get_by_filters.return_value = [sample_job_response]
    mock_job_dao.count_by_filters.return_value = 1
    
    # Call service
    result = job_service.get_jobs(db=Mock(), page=1, page_size=10)
    
    # Verify result
    assert isinstance(result, JobListResponse)
    assert result.total == 1
    assert result.page == 1
    assert result.page_size == 10
    assert result.total_pages == 1
    assert len(result.jobs) == 1
    assert result.jobs[0] == sample_job_response
    
    # Verify DAO calls
    mock_job_dao.get_by_filters.assert_called_once_with(ANY, skip=0, limit=10)
    mock_job_dao.count_by_filters.assert_called_once_with(ANY)


def test_job_service_get_jobs_with_filters(job_service, mock_job_dao, sample_job_response):
    """Test getting jobs with filters."""
    # Setup mock
    mock_job_dao.get_by_filters.return_value = [sample_job_response]
    mock_job_dao.count_by_filters.return_value = 1
    
    # Create filters
    filters = JobFilter(
        search="Engineer",
        department="Engineering",
        created_by_user_id=1
    )
    
    # Call service
    result = job_service.get_jobs(db=Mock(), page=2, page_size=5, filters=filters)
    
    # Verify result
    assert isinstance(result, JobListResponse)
    assert result.page == 2
    assert result.page_size == 5
    
    # Verify DAO calls with correct filters
    mock_job_dao.get_by_filters.assert_called_once_with(
        ANY, skip=5, limit=5, search="Engineer", department="Engineering", creator_id=1
    )
    mock_job_dao.count_by_filters.assert_called_once_with(
        ANY, search="Engineer", department="Engineering", creator_id=1
    )


def test_job_service_create_job(job_service, mock_job_dao, sample_job_response):
    """Test creating a job."""
    # Setup mock
    mock_job_dao.create.return_value = sample_job_response
    
    # Create job data
    job_create = JobCreate(
        title="Software Engineer",
        description="Develop software applications",
        department="Engineering",
        created_by_user_id=1
    )
    
    # Call service
    result = job_service.create_job(db=Mock(), job_create=job_create)
    
    # Verify result
    assert result == sample_job_response
    
    # Verify DAO call
    mock_job_dao.create.assert_called_once_with(ANY, obj_in=job_create)


def test_job_service_get_job_existing(job_service, mock_job_dao, sample_job_response):
    """Test getting an existing job."""
    # Setup mock
    mock_job_dao.get.return_value = sample_job_response
    
    # Call service
    result = job_service.get_job(db=Mock(), job_id=1)
    
    # Verify result
    assert result == sample_job_response
    
    # Verify DAO call
    mock_job_dao.get.assert_called_once_with(ANY, 1)


def test_job_service_get_job_nonexistent(job_service, mock_job_dao):
    """Test getting a non-existent job."""
    # Setup mock
    mock_job_dao.get.return_value = None
    
    # Call service
    result = job_service.get_job(db=Mock(), job_id=999)
    
    # Verify result
    assert result is None
    
    # Verify DAO call
    mock_job_dao.get.assert_called_once_with(ANY, 999)


def test_job_service_update_job_existing(job_service, mock_job_dao, sample_job_response):
    """Test updating an existing job."""
    # Setup mock
    mock_db = Mock()
    mock_db_job = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_db_job
    mock_job_dao.model = Mock()
    mock_job_dao.update.return_value = sample_job_response
    
    # Create update data
    job_update = JobUpdate(title="Senior Software Engineer")
    
    # Call service
    result = job_service.update_job(db=mock_db, job_id=1, job_update=job_update)
    
    # Verify result
    assert result == sample_job_response
    
    # Verify DAO call
    mock_job_dao.update.assert_called_once_with(ANY, db_obj=ANY, obj_in=job_update)


def test_job_service_update_job_nonexistent(job_service, mock_job_dao):
    """Test updating a non-existent job."""
    # Setup mock
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_job_dao.model = Mock()
    
    # Create update data
    job_update = JobUpdate(title="Senior Software Engineer")
    
    # Call service
    result = job_service.update_job(db=mock_db, job_id=999, job_update=job_update)
    
    # Verify result
    assert result is None
    
    # Verify DAO update was not called
    mock_job_dao.update.assert_not_called()


def test_job_service_delete_job_existing(job_service, mock_job_dao):
    """Test deleting an existing job."""
    # Setup mock
    mock_job_dao.delete.return_value = True
    
    # Call service
    result = job_service.delete_job(db=Mock(), job_id=1)
    
    # Verify result
    assert result is True
    
    # Verify DAO call
    mock_job_dao.delete.assert_called_once_with(ANY, id=1)


def test_job_service_delete_job_nonexistent(job_service, mock_job_dao):
    """Test deleting a non-existent job."""
    # Setup mock
    mock_job_dao.delete.return_value = False
    
    # Call service
    result = job_service.delete_job(db=Mock(), job_id=999)
    
    # Verify result
    assert result is False
    
    # Verify DAO call
    mock_job_dao.delete.assert_called_once_with(ANY, id=999)


def test_job_service_get_job_statistics(job_service, mock_job_dao):
    """Test getting job statistics."""
    # Setup mock
    stats = JobStatistics(
        total_interviews=10,
        avg_score=85.5,
        completion_rate=90.0,
        avg_completion_time=25.5,
        questions_count=5
    )
    mock_job_dao.get_statistics.return_value = stats
    
    # Call service
    result = job_service.get_job_statistics(db=Mock(), job_id=1)
    
    # Verify result
    assert result == stats
    
    # Verify DAO call
    mock_job_dao.get_statistics.assert_called_once_with(ANY, 1)


def test_job_service_clone_job_template_success(job_service, mock_job_dao):
    """Test successful job template cloning."""
    # Setup mock
    mock_job_dao.clone_template.return_value = True
    
    # Create clone request
    clone_request = JobCloneRequest(
        source_job_id=1,
        target_job_id=2,
        clone_questions=True
    )
    
    # Call service
    result = job_service.clone_job_template(db=Mock(), clone_request=clone_request)
    
    # Verify result
    assert result is True
    
    # Verify DAO call
    mock_job_dao.clone_template.assert_called_once_with(ANY, 1, 2)


def test_job_service_clone_job_template_skip_questions(job_service, mock_job_dao):
    """Test job template cloning when clone_questions is False."""
    # Create clone request with clone_questions=False
    clone_request = JobCloneRequest(
        source_job_id=1,
        target_job_id=2,
        clone_questions=False
    )
    
    # Call service
    result = job_service.clone_job_template(db=Mock(), clone_request=clone_request)
    
    # Verify result (should return True without calling DAO)
    assert result is True
    
    # Verify DAO was not called
    mock_job_dao.clone_template.assert_not_called()


def test_job_service_get_departments(job_service, mock_job_dao):
    """Test getting unique departments."""
    # Setup mock
    departments = ["Engineering", "Sales", "Marketing"]
    mock_job_dao.get_unique_departments.return_value = departments
    
    # Call service
    result = job_service.get_departments(db=Mock())
    
    # Verify result
    assert result == departments
    
    # Verify DAO call
    mock_job_dao.get_unique_departments.assert_called_once_with(ANY)


def test_job_service_search_jobs(job_service, mock_job_dao, sample_job_response):
    """Test searching jobs."""
    # Setup mock
    mock_job_dao.get_by_filters.return_value = [sample_job_response]
    mock_job_dao.count_by_filters.return_value = 1
    
    # Call service
    result = job_service.search_jobs(db=Mock(), search_term="Engineer", page=1, page_size=10)
    
    # Verify result
    assert isinstance(result, JobListResponse)
    assert len(result.jobs) == 1
    
    # Verify DAO calls with search filter
    mock_job_dao.get_by_filters.assert_called_once_with(ANY, skip=0, limit=10, search="Engineer")
    mock_job_dao.count_by_filters.assert_called_once_with(ANY, search="Engineer")
