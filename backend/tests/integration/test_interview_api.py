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
        "question_ids": [1]
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


def test_create_interview_success(client, auth_headers, test_candidate, test_job, test_user):
    """Test successful interview creation with required questions."""
    # First create some questions
    question1_data = {
        "title": "Criminal Background Check",
        "question_text": "Have you ever been convicted of a crime? Please provide complete details.",
        "importance": "mandatory",
        "category": "criminal_background",
        "created_by_user_id": test_user["db_user"].id
    }

    question2_data = {
        "title": "Ethics Question",
        "question_text": "Describe a time when you faced an ethical dilemma and how you handled it.",
        "importance": "ask_once",
        "category": "ethics",
        "created_by_user_id": test_user["db_user"].id
    }

    # Create questions
    q1_response = client.post("/api/v1/questions", json=question1_data, headers=auth_headers)
    q2_response = client.post("/api/v1/questions", json=question2_data, headers=auth_headers)

    assert q1_response.status_code == status.HTTP_201_CREATED
    assert q2_response.status_code == status.HTTP_201_CREATED

    question1_id = q1_response.json()["id"]
    question2_id = q2_response.json()["id"]

    interview_data = {
        "candidate_id": test_candidate["id"],
        "status": "pending",
        "question_ids": [question1_id, question2_id]
    }

    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["candidate_id"] == test_candidate["id"]
    assert data["status"] == "pending"
    assert "pass_key" in data
    assert len(data["pass_key"]) >= 8
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_interview_without_questions(client, auth_headers, test_candidate):
    """Test creating interview without questions should fail."""
    interview_data = {
        "candidate_id": test_candidate["id"],
        "status": "pending"
        # Missing question_ids
    }

    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "question_ids" in response.json()["detail"][0]["loc"]


def test_create_interview_empty_questions(client, auth_headers, test_candidate):
    """Test creating interview with empty questions list should fail."""
    interview_data = {
        "candidate_id": test_candidate["id"],
        "status": "pending",
        "question_ids": []  # Empty list
    }

    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    # Check that the error is about question_ids being too short
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("question_ids" in error.get("loc", []) for error in detail)


def test_create_interview_duplicate_questions(client, auth_headers, test_candidate, test_user):
    """Test creating interview with duplicate question IDs should fail."""
    # Create a question first
    question_data = {
        "title": "Test Question",
        "question_text": "This is a test question with sufficient length for validation.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    interview_data = {
        "candidate_id": test_candidate["id"],
        "status": "pending",
        "question_ids": [question_id, question_id]  # Duplicate IDs
    }

    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Duplicate question IDs are not allowed" in str(response.json()["detail"])


def test_create_interview_invalid_candidate(client, auth_headers, test_user):
    """Test creating interview with invalid candidate ID."""
    # Create a question first
    question_data = {
        "title": "Test Question",
        "question_text": "This is a test question with sufficient length for validation.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    interview_data = {
        "candidate_id": 99999,  # Non-existent candidate
        "question_ids": [question_id]
    }

    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Candidate not found" in response.json()["detail"]


def test_create_interview_invalid_job(client, auth_headers, test_candidate, test_user):
    """Test creating interview with invalid job ID."""
    # Create a question first
    question_data = {
        "title": "Test Question",
        "question_text": "This is a test question with sufficient length for validation.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    interview_data = {
        "candidate_id": test_candidate["id"],
        "question_ids": [question_id]
        # No job_id needed anymore since interviews are independent
    }

    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    # This should now succeed since we removed the job dependency
    assert response.status_code == status.HTTP_201_CREATED


def test_create_interview_with_questions(client, auth_headers, test_candidate, test_job, test_user):
    """Test creating interview with questions."""
    # First create some questions

    question1_data = {
        "title": "Criminal Background Check",
        "question_text": "Have you ever been convicted of a crime?",
        "importance": "mandatory",
        "category": "criminal_background",
        "created_by_user_id": test_user["db_user"].id
    }

    question2_data = {
        "title": "Ethics Question",
        "question_text": "Describe a time when you faced an ethical dilemma.",
        "importance": "ask_once",
        "category": "ethics",
        "created_by_user_id": test_user["db_user"].id
    }

    # Create questions
    q1_response = client.post("/api/v1/questions", json=question1_data, headers=auth_headers)
    q2_response = client.post("/api/v1/questions", json=question2_data, headers=auth_headers)

    assert q1_response.status_code == status.HTTP_201_CREATED
    assert q2_response.status_code == status.HTTP_201_CREATED

    question1 = q1_response.json()
    question2 = q2_response.json()

    # Create interview with questions
    interview_data = {
        "candidate_id": test_candidate["id"],
        "question_ids": [question1["id"], question2["id"]],
        "notes": "Interview with selected questions"
    }

    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["candidate_id"] == test_candidate["id"]
    assert data["analysis_notes"] == "Interview with selected questions"
    assert "pass_key" in data
    assert "id" in data

    # Verify interview questions were created
    interview_id = data["id"]

    # Get interview questions (this would require an endpoint to get interview questions)
    # For now, we'll verify the interview was created successfully
    get_response = client.get(f"/api/v1/interviews/{interview_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_200_OK


def test_create_interview_with_invalid_questions(client, auth_headers, test_candidate):
    """Test creating interview with invalid question IDs."""
    interview_data = {
        "candidate_id": test_candidate["id"],
        "question_ids": [99999, 99998]  # Non-existent questions
    }

    response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Question with ID 99999 not found" in response.json()["detail"]


def test_get_interviews_with_data(client, auth_headers, test_candidate, test_job, test_user):
    """Test getting interviews when data exists."""
    # First create a question
    question_data = {
        "title": "Test Question",
        "question_text": "This is a test question with sufficient length for validation.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create some interviews first
    for i in range(3):
        interview_data = {
            "candidate_id": test_candidate["id"],
            "question_ids": [question_id]
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


def test_get_interviews_with_status_filter(client, auth_headers, test_candidate, test_user):
    """Test getting interviews with status filtering."""
    # Create a question first
    question_data = {
        "title": "Status Test Question",
        "question_text": "This is a test question for status filtering with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create interviews with different statuses
    interview_data = {
        "candidate_id": test_candidate["id"],
        "question_ids": [question_id]
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


def test_get_interview_by_id_success(client, auth_headers, test_candidate, test_user):
    """Test getting specific interview by ID."""
    # Create a question first
    question_data = {
        "title": "Get By ID Test Question",
        "question_text": "This is a test question for get by ID test with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "question_ids": [question_id]
    }

    create_response = client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)
    created_interview = create_response.json()

    # Get interview by ID
    response = client.get(f"/api/v1/interviews/{created_interview['id']}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_interview["id"]
    assert data["candidate_id"] == test_candidate["id"]


def test_get_interview_by_id_not_found(client, auth_headers):
    """Test getting non-existent interview by ID."""
    response = client.get("/api/v1/interviews/99999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Interview not found" in response.json()["detail"]


def test_update_interview_success(client, auth_headers, test_candidate, test_user):
    """Test successful interview update."""
    # Create a question first
    question_data = {
        "title": "Update Test Question",
        "question_text": "This is a test question for update test with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "question_ids": [question_id]
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


def test_change_interview_status(client, auth_headers, test_candidate, test_user):
    """Test changing interview status."""
    # Create a question first
    question_data = {
        "title": "Status Change Test Question",
        "question_text": "This is a test question for status change test with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "question_ids": [question_id]
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


def test_cancel_interview(client, auth_headers, test_candidate, test_user):
    """Test cancelling an interview."""
    # Create a question first
    question_data = {
        "title": "Cancel Test Question",
        "question_text": "This is a test question for cancel test with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "question_ids": [question_id]
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


def test_delete_interview_success(client, auth_headers, test_candidate, test_user):
    """Test successful interview deletion."""
    # Create a question first
    question_data = {
        "title": "Delete Test Question",
        "question_text": "This is a test question for delete test with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create interview first
    interview_data = {
        "candidate_id": test_candidate["id"],
        "question_ids": [question_id]
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








def test_bulk_cancel_interviews(client, auth_headers, test_candidate, test_user):
    """Test bulk cancelling interviews."""
    # Create a question first
    question_data = {
        "title": "Bulk Cancel Test Question",
        "question_text": "This is a test question for bulk cancel test with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create multiple interviews
    interview_ids = []
    for i in range(3):
        interview_data = {
            "candidate_id": test_candidate["id"],
            "question_ids": [question_id]
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


def test_bulk_delete_interviews(client, auth_headers, test_candidate, test_user):
    """Test bulk deleting interviews."""
    # Create a question first
    question_data = {
        "title": "Bulk Delete Test Question",
        "question_text": "This is a test question for bulk delete test with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create multiple interviews
    interview_ids = []
    for i in range(2):
        interview_data = {
            "candidate_id": test_candidate["id"],
            "question_ids": [question_id]
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


def test_interviews_with_search(client, auth_headers, test_user):
    """Test searching interviews by candidate name."""
    # Create a question first
    question_data = {
        "title": "Search Test Question",
        "question_text": "This is a test question for search test with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

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
            "question_ids": [question_id]
        }
        client.post("/api/v1/interviews", json=interview_data, headers=auth_headers)

    # Search for Alice
    response = client.get("/api/v1/interviews?search=Alice", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["candidate_name"] == "Alice Johnson"


def test_interviews_with_pagination(client, auth_headers, test_candidate, test_user):
    """Test interview pagination."""
    # Create a question first
    question_data = {
        "title": "Pagination Test Question",
        "question_text": "This is a test question for pagination test with sufficient length.",
        "importance": "mandatory",
        "category": "general",
        "created_by_user_id": test_user["db_user"].id
    }

    q_response = client.post("/api/v1/questions", json=question_data, headers=auth_headers)
    assert q_response.status_code == status.HTTP_201_CREATED
    question_id = q_response.json()["id"]

    # Create 5 interviews
    for i in range(5):
        interview_data = {
            "candidate_id": test_candidate["id"],
            "question_ids": [question_id]
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
