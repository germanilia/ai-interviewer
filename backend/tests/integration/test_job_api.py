"""
Integration tests for Job API endpoints.
Tests the complete flow from HTTP request to database operations.
"""
import pytest
from fastapi import status
from app.schemas.job import JobCreate, JobUpdate
from app.schemas.user import UserCreate
from app.schemas.question import QuestionCreate
from app.schemas.job_question import JobQuestionCreate
from app.models.interview import QuestionCategory, QuestionImportance


def test_get_jobs_endpoint_requires_auth(client):
    """Test that GET /api/v1/jobs requires authentication."""
    response = client.get("/api/v1/jobs")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_job_endpoint_requires_auth(client):
    """Test that POST /api/v1/jobs requires authentication."""
    job_data = {
        "title": "Software Engineer",
        "description": "Develop software applications",
        "department": "Engineering"
    }
    response = client.post("/api/v1/jobs", json=job_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_job_endpoint_requires_auth(client):
    """Test that GET /api/v1/jobs/{id} requires authentication."""
    response = client.get("/api/v1/jobs/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_job_endpoint_requires_auth(client):
    """Test that PUT /api/v1/jobs/{id} requires authentication."""
    job_data = {
        "title": "Updated Title"
    }
    response = client.put("/api/v1/jobs/1", json=job_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_job_endpoint_requires_auth(client):
    """Test that DELETE /api/v1/jobs/{id} requires authentication."""
    response = client.delete("/api/v1/jobs/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_job_statistics_endpoint_requires_auth(client):
    """Test that GET /api/v1/jobs/{id}/statistics requires authentication."""
    response = client.get("/api/v1/jobs/1/statistics")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_job_template_endpoint_requires_auth(client):
    """Test that GET /api/v1/jobs/{id}/template requires authentication."""
    response = client.get("/api/v1/jobs/1/template")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_clone_job_template_endpoint_requires_auth(client):
    """Test that POST /api/v1/jobs/{id}/clone requires authentication."""
    clone_data = {
        "source_job_id": 1,
        "target_job_id": 2,
        "clone_questions": True
    }
    response = client.post("/api/v1/jobs/1/clone", json=clone_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_departments_endpoint_requires_auth(client):
    """Test that GET /api/v1/jobs/departments requires authentication."""
    response = client.get("/api/v1/jobs/departments")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.fixture
def auth_headers(client, test_user, mock_cognito):
    """Create authentication headers for testing."""
    # Sign in user to get token using the API endpoint
    signin_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }

    signin_response = client.post("/api/v1/auth/signin", json=signin_data)
    assert signin_response.status_code == 200

    access_token = signin_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_create_job_success(client, auth_headers):
    """Test successful job creation via API."""
    job_data = {
        "title": "Software Engineer",
        "description": "Develop and maintain software applications",
        "department": "Engineering"
    }

    response = client.post(
        "/api/v1/jobs",
        json=job_data,
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == job_data["title"]
    assert data["description"] == job_data["description"]
    assert data["department"] == job_data["department"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_job_missing_title(client, auth_headers):
    """Test job creation with missing required title."""
    job_data = {
        "description": "Some description",
        "department": "Engineering"
    }

    response = client.post(
        "/api/v1/jobs",
        json=job_data,
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_jobs_empty_list(client, auth_headers):
    """Test getting jobs when none exist."""
    response = client.get("/api/v1/jobs", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["jobs"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 0


def test_get_jobs_with_data(client, auth_headers):
    """Test getting jobs when data exists."""
    # Create some jobs first
    jobs_data = [
        {"title": "Frontend Developer", "description": "Build UIs", "department": "Engineering"},
        {"title": "Backend Developer", "description": "Build APIs", "department": "Engineering"},
        {"title": "Product Manager", "description": "Manage products", "department": "Product"}
    ]

    for job_data in jobs_data:
        client.post("/api/v1/jobs", json=job_data, headers=auth_headers)

    # Get jobs
    response = client.get("/api/v1/jobs", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["jobs"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 1


def test_get_jobs_with_pagination(client, auth_headers):
    """Test getting jobs with pagination."""
    # Create 5 jobs
    for i in range(5):
        job_data = {
            "title": f"Job {i}",
            "description": f"Description {i}",
            "department": "Engineering"
        }
        client.post("/api/v1/jobs", json=job_data, headers=auth_headers)

    # Get first page
    response = client.get("/api/v1/jobs?page=1&page_size=2", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["jobs"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 3


def test_get_jobs_with_search_using_dao(client, db, auth_headers, job_dao, user_dao):
    """Test getting jobs with search filter using DAO."""
    # Create a user first
    user_create = UserCreate(
        username="testuser_search",
        email="testsearch@example.com",
        full_name="Test Search User"
    )
    created_user = user_dao.create(db, obj_in=user_create)

    # Create test jobs using DAO
    jobs_data = [
        {"title": "Senior Python Developer", "department": "Engineering"},
        {"title": "Junior Java Developer", "department": "Engineering"},
        {"title": "Product Manager", "department": "Product"}
    ]

    for job_data in jobs_data:
        job_create = JobCreate(
            **job_data,
            created_by_user_id=created_user.id
        )
        job_dao.create(db, obj_in=job_create)

    # Search for "Developer"
    response = client.get("/api/v1/jobs?search=Developer", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["jobs"]) == 2  # Should find 2 developer jobs
    for job in data["jobs"]:
        assert "Developer" in job["title"]


def test_get_jobs_with_department_filter_using_dao(client, db, auth_headers, job_dao, user_dao):
    """Test getting jobs with department filter using DAO."""
    # Create a user first
    user_create = UserCreate(
        username="testuser_dept",
        email="testdept@example.com",
        full_name="Test Dept User"
    )
    created_user = user_dao.create(db, obj_in=user_create)

    # Create test jobs using DAO
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

    # Filter by Engineering department
    response = client.get("/api/v1/jobs?department=Engineering", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["jobs"]) == 2  # Should find 2 engineering jobs
    for job in data["jobs"]:
        assert job["department"] == "Engineering"


def test_get_job_by_id_using_dao(client, db, auth_headers, job_dao, user_dao):
    """Test getting a specific job by ID using DAO."""
    # Create a user and job using DAO
    user_create = UserCreate(
        username="testuser_getjob",
        email="testgetjob@example.com",
        full_name="Test Get Job User"
    )
    created_user = user_dao.create(db, obj_in=user_create)

    job_create = JobCreate(
        title="Test Job",
        description="Test description",
        department="Test Department",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)

    # Get job by ID
    response = client.get(f"/api/v1/jobs/{created_job.id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_job.id
    assert data["title"] == "Test Job"
    assert data["description"] == "Test description"
    assert data["department"] == "Test Department"


def test_get_job_by_id_not_found(client, auth_headers):
    """Test getting a non-existent job."""
    response = client.get("/api/v1/jobs/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_job_using_dao(client, db, auth_headers, job_dao, user_dao):
    """Test updating a job via API using DAO."""
    # Create a user and job using DAO
    user_create = UserCreate(
        username="testuser_update",
        email="testupdate@example.com",
        full_name="Test Update User"
    )
    created_user = user_dao.create(db, obj_in=user_create)

    job_create = JobCreate(
        title="Original Title",
        description="Original description",
        department="Original Department",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)

    # Update job
    update_data = {
        "title": "Updated Title",
        "department": "Updated Department"
    }

    response = client.put(
        f"/api/v1/jobs/{created_job.id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Original description"  # Unchanged
    assert data["department"] == "Updated Department"


def test_update_job_not_found(client, auth_headers):
    """Test updating a non-existent job."""
    update_data = {"title": "Updated Title"}

    response = client.put(
        "/api/v1/jobs/99999",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_job_using_dao(client, db, auth_headers, job_dao, user_dao):
    """Test deleting a job via API using DAO."""
    # Create a user and job using DAO
    user_create = UserCreate(
        username="testuser_delete",
        email="testdelete@example.com",
        full_name="Test Delete User"
    )
    created_user = user_dao.create(db, obj_in=user_create)

    job_create = JobCreate(
        title="Job to Delete",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)

    # Delete job
    response = client.delete(f"/api/v1/jobs/{created_job.id}", headers=auth_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify job is deleted
    get_response = client.get(f"/api/v1/jobs/{created_job.id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_job_not_found_dao(client, auth_headers):
    """Test deleting a non-existent job using DAO."""
    response = client.delete("/api/v1/jobs/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_job_statistics_using_dao(client, db, auth_headers, job_dao, user_dao):
    """Test getting job statistics via API using DAO."""
    # Create a user and job using DAO
    user_create = UserCreate(
        username="testuser_stats",
        email="teststats@example.com",
        full_name="Test Stats User"
    )
    created_user = user_dao.create(db, obj_in=user_create)

    job_create = JobCreate(
        title="Job for Stats",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)

    # Get statistics
    response = client.get(f"/api/v1/jobs/{created_job.id}/statistics", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_interviews" in data
    assert "avg_score" in data
    assert "completion_rate" in data
    assert "avg_completion_time" in data
    assert "questions_count" in data

    # For a new job, should have zero statistics
    assert data["total_interviews"] == 0
    assert data["avg_score"] is None
    assert data["completion_rate"] == 0.0
    assert data["questions_count"] == 0


def test_get_departments_using_dao(client, db, auth_headers, job_dao, user_dao):
    """Test getting unique departments via API using DAO."""
    # Create a user first
    user_create = UserCreate(
        username="testuser_depts",
        email="testdepts@example.com",
        full_name="Test Depts User"
    )
    created_user = user_dao.create(db, obj_in=user_create)

    # Create jobs in different departments using DAO
    departments = ["Engineering", "Sales", "Marketing"]
    for dept in departments:
        job_create = JobCreate(
            title=f"Job in {dept}",
            department=dept,
            created_by_user_id=created_user.id
        )
        job_dao.create(db, obj_in=job_create)

    # Get departments
    response = client.get("/api/v1/jobs/departments", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert set(departments).issubset(set(data))  # Should include our departments


def test_get_jobs_with_search(client, db, auth_headers, job_dao, user_dao):
    """Test getting jobs with search filter."""
    # Create a user first
    user_create = UserCreate(
        username="testuser3",
        email="test3@example.com",
        full_name="Test User 3"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create test jobs
    jobs_data = [
        {"title": "Senior Python Developer", "department": "Engineering"},
        {"title": "Junior Java Developer", "department": "Engineering"},
        {"title": "Product Manager", "department": "Product"}
    ]
    
    for job_data in jobs_data:
        job_create = JobCreate(
            **job_data,
            created_by_user_id=created_user.id
        )
        job_dao.create(db, obj_in=job_create)
    
    # Search for "Developer"
    response = client.get(
        "/api/v1/jobs?search=Developer",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["jobs"]) == 2  # Should find 2 developer jobs
    for job in data["jobs"]:
        assert "Developer" in job["title"]


def test_get_jobs_with_department_filter(client, db, auth_headers, job_dao, user_dao):
    """Test getting jobs with department filter."""
    # Create a user first
    user_create = UserCreate(
        username="testuser4",
        email="test4@example.com",
        full_name="Test User 4"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create test jobs
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
    
    # Filter by Engineering department
    response = client.get(
        "/api/v1/jobs?department=Engineering",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["jobs"]) == 2  # Should find 2 engineering jobs
    for job in data["jobs"]:
        assert job["department"] == "Engineering"


def test_get_job_by_id(client, db, auth_headers, job_dao, user_dao):
    """Test getting a specific job by ID."""
    # Create a user and job
    user_create = UserCreate(
        username="testuser5",
        email="test5@example.com",
        full_name="Test User 5"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Test Job",
        description="Test description",
        department="Test Department",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Get job by ID
    response = client.get(f"/api/v1/jobs/{created_job.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_job.id
    assert data["title"] == "Test Job"
    assert data["description"] == "Test description"
    assert data["department"] == "Test Department"

def test_update_job(client, db, auth_headers, job_dao, user_dao):
    """Test updating a job via API."""
    # Create a user and job
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
    
    # Update job
    update_data = {
        "title": "Updated Title",
        "department": "Updated Department"
    }
    
    response = client.put(
        f"/api/v1/jobs/{created_job.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Original description"  # Unchanged
    assert data["department"] == "Updated Department"


def test_delete_job(client, db, auth_headers, job_dao, user_dao):
    """Test deleting a job via API."""
    # Create a user and job
    user_create = UserCreate(
        username="testuser7",
        email="test7@example.com",
        full_name="Test User 7"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Job to Delete",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Delete job
    response = client.delete(f"/api/v1/jobs/{created_job.id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify job is deleted
    get_response = client.get(f"/api/v1/jobs/{created_job.id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_job_not_found(client, auth_headers):
    """Test deleting a non-existent job."""
    response = client.delete("/api/v1/jobs/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_job_statistics(client, db, auth_headers, job_dao, user_dao):
    """Test getting job statistics via API."""
    # Create a user and job
    user_create = UserCreate(
        username="testuser8",
        email="test8@example.com",
        full_name="Test User 8"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    job_create = JobCreate(
        title="Job for Stats",
        created_by_user_id=created_user.id
    )
    created_job = job_dao.create(db, obj_in=job_create)
    
    # Get statistics
    response = client.get(f"/api/v1/jobs/{created_job.id}/statistics", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total_interviews" in data
    assert "avg_score" in data
    assert "completion_rate" in data
    assert "avg_completion_time" in data
    assert "questions_count" in data
    
    # For a new job, should have zero statistics
    assert data["total_interviews"] == 0
    assert data["avg_score"] is None
    assert data["completion_rate"] == 0.0
    assert data["questions_count"] == 0


def test_get_departments(client, db, auth_headers, job_dao, user_dao):
    """Test getting unique departments via API."""
    # Create a user first
    user_create = UserCreate(
        username="testuser9",
        email="test9@example.com",
        full_name="Test User 9"
    )
    created_user = user_dao.create(db, obj_in=user_create)
    
    # Create jobs in different departments
    departments = ["Engineering", "Sales", "Marketing"]
    for dept in departments:
        job_create = JobCreate(
            title=f"Job in {dept}",
            department=dept,
            created_by_user_id=created_user.id
        )
        job_dao.create(db, obj_in=job_create)
    
    # Get departments
    response = client.get("/api/v1/jobs/departments", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert set(departments).issubset(set(data))  # Should include our departments
