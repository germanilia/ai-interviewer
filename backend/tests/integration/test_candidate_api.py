"""
Integration tests for Candidate API endpoints.
"""
import pytest
from fastapi import status


def test_get_candidates_endpoint_requires_auth(client):
    """Test that GET /api/v1/candidates requires authentication."""
    response = client.get("/api/v1/candidates")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_candidate_endpoint_requires_auth(client):
    """Test that POST /api/v1/candidates requires authentication."""
    candidate_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com"
    }
    response = client.post("/api/v1/candidates", json=candidate_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_candidate_endpoint_requires_auth(client):
    """Test that GET /api/v1/candidates/{id} requires authentication."""
    response = client.get("/api/v1/candidates/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_candidate_endpoint_requires_auth(client):
    """Test that PUT /api/v1/candidates/{id} requires authentication."""
    candidate_data = {
        "first_name": "Updated"
    }
    response = client.put("/api/v1/candidates/1", json=candidate_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_candidate_endpoint_requires_auth(client):
    """Test that DELETE /api/v1/candidates/{id} requires authentication."""
    response = client.delete("/api/v1/candidates/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_candidate_interviews_endpoint_requires_auth(client):
    """Test that GET /api/v1/candidates/{id}/interviews requires authentication."""
    response = client.get("/api/v1/candidates/1/interviews")
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


def test_create_candidate_success(client, auth_headers):
    """Test successful candidate creation."""
    candidate_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890"
    }
    
    response = client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["phone"] == "+1234567890"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_candidate_without_phone(client, auth_headers):
    """Test creating candidate without phone number."""
    candidate_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com"
    }
    
    response = client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["email"] == "jane.smith@example.com"
    assert data["phone"] is None


def test_create_candidate_duplicate_email(client, auth_headers):
    """Test creating candidate with duplicate email returns error."""
    candidate_data = {
        "first_name": "First",
        "last_name": "User",
        "email": "duplicate@example.com"
    }
    
    # Create first candidate
    response1 = client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Try to create second candidate with same email
    duplicate_data = {
        "first_name": "Second",
        "last_name": "User",
        "email": "duplicate@example.com"
    }
    
    response2 = client.post("/api/v1/candidates", json=duplicate_data, headers=auth_headers)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already exists" in response2.json()["detail"]


def test_create_candidate_invalid_data(client, auth_headers):
    """Test creating candidate with invalid data."""
    # Missing required fields
    invalid_data = {
        "first_name": "John"
        # Missing last_name and email
    }
    
    response = client.post("/api/v1/candidates", json=invalid_data, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_candidates_empty_list(client, auth_headers):
    """Test getting candidates when none exist."""
    response = client.get("/api/v1/candidates", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 0


def test_get_candidates_with_data(client, auth_headers):
    """Test getting candidates when data exists."""
    # Create some candidates first
    candidates_data = [
        {"first_name": "Alice", "last_name": "Johnson", "email": "alice@example.com"},
        {"first_name": "Bob", "last_name": "Wilson", "email": "bob@example.com"},
        {"first_name": "Carol", "last_name": "Brown", "email": "carol@example.com"}
    ]
    
    for candidate_data in candidates_data:
        client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    
    # Get candidates
    response = client.get("/api/v1/candidates", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 1


def test_get_candidates_with_pagination(client, auth_headers):
    """Test getting candidates with pagination."""
    # Create 5 candidates
    for i in range(5):
        candidate_data = {
            "first_name": f"User{i}",
            "last_name": f"Test{i}",
            "email": f"user{i}@example.com"
        }
        client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    
    # Get first page
    response = client.get("/api/v1/candidates?page=1&page_size=2", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 3


def test_get_candidates_with_search(client, auth_headers):
    """Test getting candidates with search functionality."""
    # Create candidates with different names
    candidates_data = [
        {"first_name": "John", "last_name": "Smith", "email": "john.smith@example.com"},
        {"first_name": "Jane", "last_name": "Johnson", "email": "jane.johnson@example.com"},
        {"first_name": "Bob", "last_name": "Smith", "email": "bob.smith@example.com"}
    ]
    
    for candidate_data in candidates_data:
        client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    
    # Search by last name
    response = client.get("/api/v1/candidates?search=Smith", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2  # John Smith and Bob Smith
    assert data["total"] == 2


def test_get_candidate_by_id_success(client, auth_headers):
    """Test getting specific candidate by ID."""
    # Create candidate first
    candidate_data = {
        "first_name": "Get",
        "last_name": "Test",
        "email": "get.test@example.com"
    }
    
    create_response = client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    created_candidate = create_response.json()
    
    # Get candidate by ID
    response = client.get(f"/api/v1/candidates/{created_candidate['id']}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_candidate["id"]
    assert data["first_name"] == "Get"
    assert data["last_name"] == "Test"
    assert data["email"] == "get.test@example.com"


def test_get_candidate_by_id_not_found(client, auth_headers):
    """Test getting non-existent candidate by ID."""
    response = client.get("/api/v1/candidates/99999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Candidate not found" in response.json()["detail"]


def test_update_candidate_success(client, auth_headers):
    """Test successful candidate update."""
    # Create candidate first
    candidate_data = {
        "first_name": "Original",
        "last_name": "Name",
        "email": "original@example.com",
        "phone": "+1111111111"
    }
    
    create_response = client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    created_candidate = create_response.json()
    
    # Update candidate
    update_data = {
        "first_name": "Updated",
        "phone": "+2222222222"
    }
    
    response = client.put(f"/api/v1/candidates/{created_candidate['id']}", json=update_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"  # Unchanged
    assert data["email"] == "original@example.com"  # Unchanged
    assert data["phone"] == "+2222222222"


def test_update_candidate_not_found(client, auth_headers):
    """Test updating non-existent candidate."""
    update_data = {
        "first_name": "Updated"
    }

    response = client.put("/api/v1/candidates/99999", json=update_data, headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Candidate not found" in response.json()["detail"]


def test_delete_candidate_success(client, auth_headers):
    """Test successful candidate deletion."""
    # Create candidate first
    candidate_data = {
        "first_name": "Delete",
        "last_name": "Me",
        "email": "delete@example.com"
    }
    
    create_response = client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    created_candidate = create_response.json()
    
    # Delete candidate
    response = client.delete(f"/api/v1/candidates/{created_candidate['id']}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify candidate is deleted
    get_response = client.get(f"/api/v1/candidates/{created_candidate['id']}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_candidate_not_found(client, auth_headers):
    """Test deleting non-existent candidate."""
    response = client.delete("/api/v1/candidates/99999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Candidate not found" in response.json()["detail"]


def test_get_candidate_interviews_success(client, auth_headers):
    """Test getting candidate interview history."""
    # Create candidate first
    candidate_data = {
        "first_name": "Interview",
        "last_name": "Test",
        "email": "interview@example.com"
    }
    
    create_response = client.post("/api/v1/candidates", json=candidate_data, headers=auth_headers)
    created_candidate = create_response.json()
    
    # Get interview history
    response = client.get(f"/api/v1/candidates/{created_candidate['id']}/interviews", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["candidate_id"] == created_candidate["id"]
    assert data["interviews"] == []  # No interviews yet


def test_get_candidate_interviews_not_found(client, auth_headers):
    """Test getting interview history for non-existent candidate."""
    response = client.get("/api/v1/candidates/99999/interviews", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Candidate not found" in response.json()["detail"]
