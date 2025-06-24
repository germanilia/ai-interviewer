"""
Integration tests for Interview API endpoints.
"""
import pytest
from fastapi import status


def test_get_interviews_endpoint_requires_auth(client):
    """Test that GET /api/v1/interviews requires authentication."""
    response = client.get("/api/v1/interviews")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_interview_endpoint_requires_auth(client):
    """Test that POST /api/v1/interviews requires authentication."""
    interview_data = {
        "candidate_id": 1,
        "job_id": 1
    }
    response = client.post("/api/v1/interviews", json=interview_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_interview_endpoint_requires_auth(client):
    """Test that GET /api/v1/interviews/{id} requires authentication."""
    response = client.get("/api/v1/interviews/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_interview_endpoint_requires_auth(client):
    """Test that PUT /api/v1/interviews/{id} requires authentication."""
    interview_data = {
        "status": "in_progress"
    }
    response = client.put("/api/v1/interviews/1", json=interview_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_interview_endpoint_requires_auth(client):
    """Test that DELETE /api/v1/interviews/{id} requires authentication."""
    response = client.delete("/api/v1/interviews/1")
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


@pytest.fixture
def test_candidate(client, auth_headers):
    """Create a test candidate for interview tests."""
    candidate_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890"
    }
    
    response = client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


@pytest.fixture
def test_job(db, test_user):
    """Create a test job for interview tests."""
    from app.models.interview import Job

    # Create job directly using SQLAlchemy model
    job = Job(
        title="Software Engineer",
        description="Test job description",
        department="Engineering",
        created_by_user_id=test_user["db_user"].id
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Return as dict for compatibility
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "department": job.department,
        "created_by_user_id": job.created_by_user_id,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat()
    }


def test_get_interviews_empty_list(client, auth_headers):
    """Test getting interviews when none exist."""
    response = client.get("/api/v1/interviews", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 0


def test_create_interview_success(client, auth_headers, test_candidate, test_job):
    """Test successful interview creation."""
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": test_job["id"],
        "status": "pending"
    }
    
    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["candidate_id"] == test_candidate["id"]
    assert data["job_id"] == test_job["id"]
    assert data["status"] == "pending"
    assert "pass_key" in data
    assert len(data["pass_key"]) >= 8
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_interview_invalid_candidate(client, auth_headers, test_job):
    """Test creating interview with invalid candidate ID."""
    interview_data = {
        "candidate_id": 99999,  # Non-existent candidate
        "job_id": test_job["id"]
    }
    
    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Candidate not found" in response.json()["detail"]


def test_create_interview_invalid_job(client, auth_headers, test_candidate):
    """Test creating interview with invalid job ID."""
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": 99999  # Non-existent job
    }
    
    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Job not found" in response.json()["detail"]


def test_get_interviews_with_data(client, auth_headers, test_candidate, test_job):
    """Test getting interviews when data exists."""
    # Create some interviews first
    for i in range(3):
        interview_data = {
            "candidate_id": test_candidate["id"],
            "job_id": test_job["id"]
        }
        client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    
    # Get interviews
    response = client.get("/api/v1/interviews", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 1
    
    # Check that status counts are included
    assert "status_counts" in data
    assert "all" in data["status_counts"]
    assert "pending" in data["status_counts"]


def test_get_interviews_with_status_filter(client, auth_headers, test_candidate, test_job):
    """Test getting interviews with status filtering."""
    # Create interviews with different statuses
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": test_job["id"]
    }

    # Create pending interview
    response1 = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    interview1 = response1.json()

    # Create another interview and change its status
    response2 = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    interview2 = response2.json()

    # Change second interview to in_progress
    status_data = {
        "status": "in_progress"
    }
    update_response = client.put(f"/api/v1/interviews/{interview2['id']}", json=status_data, headers=auth_headers)

    # Verify the update worked
    assert update_response.status_code == status.HTTP_200_OK
    updated_interview = update_response.json()
    assert updated_interview["status"] == "in_progress"

    # First, get all interviews to see what we have
    all_response = client.get("/api/v1/interviews", headers=auth_headers)
    all_data = all_response.json()
    assert len(all_data["items"]) == 2

    # Check the statuses of both interviews
    statuses = [item["status"] for item in all_data["items"]]
    assert "pending" in statuses
    assert "in_progress" in statuses

    # Filter by pending status
    response = client.get("/api/v1/interviews?status=pending", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Debug: if this fails, let's see what we got
    if len(data["items"]) != 1:
        print(f"Expected 1 pending interview, got {len(data['items'])}")
        for item in data["items"]:
            print(f"  Interview {item['id']}: status={item['status']}")

    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "pending"


def test_get_interview_by_id_success(client, auth_headers, test_candidate, test_job):
    """Test getting specific interview by ID."""
    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": test_job["id"]
    }
    
    create_response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    created_interview = create_response.json()
    
    # Get interview by ID
    response = client.get(f"/api/v1/interviews/{created_interview['id']}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_interview["id"]
    assert data["candidate_id"] == test_candidate["id"]
    assert data["job_id"] == test_job["id"]


def test_get_interview_by_id_not_found(client, auth_headers):
    """Test getting non-existent interview by ID."""
    response = client.get("/api/v1/interviews/99999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Interview not found" in response.json()["detail"]


def test_update_interview_success(client, auth_headers, test_candidate, test_job):
    """Test successful interview update."""
    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": test_job["id"]
    }
    
    create_response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    created_interview = create_response.json()
    
    # Update interview
    update_data = {
        "status": "in_progress",
        "score": 85
    }
    
    response = client.put(f"/api/v1/interviews/{created_interview['id']}", json=update_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["score"] == 85


def test_update_interview_not_found(client, auth_headers):
    """Test updating non-existent interview."""
    update_data = {
        "status": "completed"
    }

    response = client.put("/api/v1/interviews/99999", json=update_data, headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Interview not found" in response.json()["detail"]


def test_change_interview_status(client, auth_headers, test_candidate, test_job):
    """Test changing interview status."""
    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": test_job["id"]
    }
    
    create_response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    created_interview = create_response.json()
    
    # Change status
    response = client.patch(
        f"/api/v1/interviews/{created_interview['id']}/status?new_status=in_progress&reason=Starting interview",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "in_progress"


def test_cancel_interview(client, auth_headers, test_candidate, test_job):
    """Test cancelling an interview."""
    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": test_job["id"]
    }
    
    create_response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    created_interview = create_response.json()
    
    # Cancel interview
    response = client.patch(
        f"/api/v1/interviews/{created_interview['id']}/cancel",
        json="Candidate withdrew application",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "cancelled"


def test_delete_interview_success(client, auth_headers, test_candidate, test_job):
    """Test successful interview deletion."""
    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": test_job["id"]
    }
    
    create_response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    created_interview = create_response.json()
    
    # Delete interview
    response = client.delete(f"/api/v1/interviews/{created_interview['id']}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert "deleted successfully" in response.json()["message"]
    
    # Verify interview is deleted
    get_response = client.get(f"/api/v1/interviews/{created_interview['id']}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_interview_not_found(client, auth_headers):
    """Test deleting non-existent interview."""
    response = client.delete("/api/v1/interviews/99999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Interview not found" in response.json()["detail"]





def test_get_interview_monitoring_data(client, auth_headers, test_candidate, test_job):
    """Test getting monitoring data for in-progress interview."""
    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": test_job["id"]
    }

    create_response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    created_interview = create_response.json()

    # Change status to in_progress
    status_data = {
        "status": "in_progress"
    }
    client.put(f"/api/v1/interviews/{created_interview['id']}", json=status_data, headers=auth_headers)

    # Get monitoring data
    response = client.get(f"/api/v1/interviews/{created_interview['id']}/monitor", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["interview_id"] == created_interview["id"]
    assert data["status"] == "in_progress"
    assert "progress" in data
    assert "time_elapsed" in data


def test_get_monitoring_data_not_in_progress(client, auth_headers, test_candidate, test_job):
    """Test getting monitoring data for interview not in progress."""
    # Create interview (default status is pending)
    interview_data = {
        "candidate_id": test_candidate["id"],
        "job_id": test_job["id"]
    }

    create_response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    created_interview = create_response.json()

    # Try to get monitoring data for pending interview
    response = client.get(f"/api/v1/interviews/{created_interview['id']}/monitor", headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not in progress" in response.json()["detail"]


def test_bulk_cancel_interviews(client, auth_headers, test_candidate, test_job):
    """Test bulk cancelling interviews."""
    # Create multiple interviews
    interview_ids = []
    for i in range(3):
        interview_data = {
            "candidate_id": test_candidate["id"],
            "job_id": test_job["id"]
        }
        response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
        interview_ids.append(response.json()["id"])

    # Bulk cancel
    bulk_data = {
        "interview_ids": interview_ids,
        "reason": "Bulk cancellation test"
    }

    response = client.post("/api/v1/interviews/bulk/cancel", json=bulk_data, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["results"]) == 3

    # Verify all were cancelled
    for result in data["results"]:
        assert result["status"] == "cancelled"


def test_bulk_delete_interviews(client, auth_headers, test_candidate, test_job):
    """Test bulk deleting interviews."""
    # Create multiple interviews
    interview_ids = []
    for i in range(2):
        interview_data = {
            "candidate_id": test_candidate["id"],
            "job_id": test_job["id"]
        }
        response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
        interview_ids.append(response.json()["id"])

    # Bulk delete
    response = client.post("/api/v1/interviews/bulk/delete", json=interview_ids, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["results"]) == 2

    # Verify all were deleted
    for result in data["results"]:
        assert result["status"] == "deleted"


def test_interviews_with_search(client, auth_headers, test_job):
    """Test searching interviews by candidate name."""
    # Create candidates with different names
    candidate1_data = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice.johnson@example.com"
    }
    candidate2_data = {
        "first_name": "Bob",
        "last_name": "Smith",
        "email": "bob.smith@example.com"
    }

    candidate1_response = client.post("/api/v1/candidates", json=candidate1_data, headers=auth_headers)
    candidate2_response = client.post("/api/v1/candidates", json=candidate2_data, headers=auth_headers)

    candidate1 = candidate1_response.json()
    candidate2 = candidate2_response.json()

    # Create interviews for both candidates
    for candidate in [candidate1, candidate2]:
        interview_data = {
            "candidate_id": candidate["id"],
            "job_id": test_job["id"]
        }
        client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)

    # Search for Alice
    response = client.get("/api/v1/interviews?search=Alice", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["candidate_name"] == "Alice Johnson"


def test_interviews_with_pagination(client, auth_headers, test_candidate, test_job):
    """Test interview pagination."""
    # Create 5 interviews
    for i in range(5):
        interview_data = {
            "candidate_id": test_candidate["id"],
            "job_id": test_job["id"]
        }
        client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)

    # Get first page
    response = client.get("/api/v1/interviews?page=1&page_size=2", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 3
