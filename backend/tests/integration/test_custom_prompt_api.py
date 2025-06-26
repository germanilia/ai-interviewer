"""
Integration tests for Custom Prompt API endpoints.
Tests the complete flow from HTTP request to database operations.
"""
import pytest
from fastapi import status
from app.models.custom_prompt import PromptType


def test_get_custom_prompts_requires_auth(client):
    """Test that GET /api/v1/custom-prompts requires authentication."""
    response = client.get("/api/v1/custom-prompts")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_custom_prompt_requires_auth(client):
    """Test that POST /api/v1/custom-prompts requires authentication."""
    prompt_data = {
        "prompt_type": "evaluation",
        "name": "Test Prompt",
        "content": "Test content",
        "created_by_user_id": 1
    }
    response = client.post("/api/v1/custom-prompts", json=prompt_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_custom_prompts_empty_list(authenticated_client):
    """Test GET /api/v1/custom-prompts returns empty list when no prompts exist."""
    response = authenticated_client.get("/api/v1/custom-prompts")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "prompts" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert data["prompts"] == []
    assert data["total"] == 0


def test_create_custom_prompt_success(authenticated_client, test_user):
    """Test successful creation of a custom prompt."""
    prompt_data = {
        "prompt_type": "evaluation",
        "name": "Test Evaluation Prompt",
        "content": "You are a test prompt for {candidate_name}",
        "description": "A test prompt for integration testing",
        "is_active": True,
        "created_by_user_id": test_user["id"]
    }
    
    response = authenticated_client.post("/api/v1/custom-prompts", json=prompt_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["prompt_type"] == "evaluation"
    assert data["name"] == "Test Evaluation Prompt"
    assert data["content"] == "You are a test prompt for {candidate_name}"
    assert data["description"] == "A test prompt for integration testing"
    assert data["is_active"] is True
    assert data["created_by_user_id"] == test_user["id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_custom_prompt_validation_error(authenticated_client, test_user):
    """Test custom prompt creation with validation errors."""
    # Missing required fields
    prompt_data = {
        "prompt_type": "evaluation",
        # Missing name and content
        "created_by_user_id": test_user["id"]
    }
    
    response = authenticated_client.post("/api/v1/custom-prompts", json=prompt_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_custom_prompt_by_id(authenticated_client, test_user):
    """Test GET /api/v1/custom-prompts/{id}."""
    # Create a prompt first
    prompt_data = {
        "prompt_type": "judge",
        "name": "Test Judge Prompt",
        "content": "You are a judge prompt",
        "created_by_user_id": test_user["id"]
    }
    
    create_response = authenticated_client.post("/api/v1/custom-prompts", json=prompt_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    created_prompt = create_response.json()
    
    # Get the prompt by ID
    response = authenticated_client.get(f"/api/v1/custom-prompts/{created_prompt['id']}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == created_prompt["id"]
    assert data["name"] == "Test Judge Prompt"
    assert data["prompt_type"] == "judge"


def test_get_custom_prompt_not_found(authenticated_client):
    """Test GET /api/v1/custom-prompts/{id} with non-existent ID."""
    response = authenticated_client.get("/api/v1/custom-prompts/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_custom_prompt(authenticated_client, test_user):
    """Test PUT /api/v1/custom-prompts/{id}."""
    # Create a prompt first
    prompt_data = {
        "prompt_type": "guardrails",
        "name": "Original Guardrails Prompt",
        "content": "Original content",
        "created_by_user_id": test_user["id"]
    }
    
    create_response = authenticated_client.post("/api/v1/custom-prompts", json=prompt_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    created_prompt = create_response.json()
    
    # Update the prompt
    update_data = {
        "name": "Updated Guardrails Prompt",
        "content": "Updated content",
        "is_active": False
    }
    
    response = authenticated_client.put(f"/api/v1/custom-prompts/{created_prompt['id']}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == created_prompt["id"]
    assert data["name"] == "Updated Guardrails Prompt"
    assert data["content"] == "Updated content"
    assert data["is_active"] is False


def test_update_custom_prompt_not_found(authenticated_client):
    """Test PUT /api/v1/custom-prompts/{id} with non-existent ID."""
    update_data = {
        "name": "Updated Name"
    }
    
    response = authenticated_client.put("/api/v1/custom-prompts/99999", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_custom_prompt(authenticated_client, test_user):
    """Test DELETE /api/v1/custom-prompts/{id}."""
    # Create a prompt first
    prompt_data = {
        "prompt_type": "evaluation",
        "name": "Prompt to Delete",
        "content": "This will be deleted",
        "created_by_user_id": test_user["id"]
    }
    
    create_response = authenticated_client.post("/api/v1/custom-prompts", json=prompt_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    created_prompt = create_response.json()
    
    # Delete the prompt
    response = authenticated_client.delete(f"/api/v1/custom-prompts/{created_prompt['id']}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "message" in data
    assert "deleted successfully" in data["message"]
    
    # Verify the prompt is deleted
    get_response = authenticated_client.get(f"/api/v1/custom-prompts/{created_prompt['id']}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_custom_prompt_not_found(authenticated_client):
    """Test DELETE /api/v1/custom-prompts/{id} with non-existent ID."""
    response = authenticated_client.delete("/api/v1/custom-prompts/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_activate_custom_prompt(authenticated_client, test_user):
    """Test POST /api/v1/custom-prompts/{id}/activate."""
    # Create multiple prompts of the same type
    prompt_ids = []
    for i in range(3):
        prompt_data = {
            "prompt_type": "evaluation",
            "name": f"Evaluation Prompt {i}",
            "content": f"Content {i}",
            "is_active": (i == 0),  # Only first one is initially active
            "created_by_user_id": test_user["id"]
        }
        
        create_response = authenticated_client.post("/api/v1/custom-prompts", json=prompt_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        prompt_ids.append(create_response.json()["id"])
    
    # Activate the second prompt
    response = authenticated_client.post(f"/api/v1/custom-prompts/{prompt_ids[1]}/activate")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == prompt_ids[1]
    assert data["is_active"] is True
    
    # Verify others are deactivated
    for i, prompt_id in enumerate(prompt_ids):
        get_response = authenticated_client.get(f"/api/v1/custom-prompts/{prompt_id}")
        prompt_data = get_response.json()
        if i == 1:
            assert prompt_data["is_active"] is True
        else:
            assert prompt_data["is_active"] is False


def test_get_active_prompt_by_type(authenticated_client, test_user):
    """Test GET /api/v1/custom-prompts/types/{type}/active."""
    # Create prompts of different types
    prompt_data = {
        "prompt_type": "judge",
        "name": "Active Judge Prompt",
        "content": "Active judge content",
        "is_active": True,
        "created_by_user_id": test_user["id"]
    }
    
    create_response = authenticated_client.post("/api/v1/custom-prompts", json=prompt_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    created_prompt = create_response.json()
    
    # Get active prompt by type
    response = authenticated_client.get("/api/v1/custom-prompts/types/judge/active")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == created_prompt["id"]
    assert data["prompt_type"] == "judge"
    assert data["is_active"] is True


def test_get_active_prompt_by_type_none_active(authenticated_client, test_user):
    """Test GET /api/v1/custom-prompts/types/{type}/active when no prompts are active."""
    # Create inactive prompt
    prompt_data = {
        "prompt_type": "guardrails",
        "name": "Inactive Guardrails Prompt",
        "content": "Inactive content",
        "is_active": False,
        "created_by_user_id": test_user["id"]
    }
    
    create_response = authenticated_client.post("/api/v1/custom-prompts", json=prompt_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    
    # Try to get active prompt
    response = authenticated_client.get("/api/v1/custom-prompts/types/guardrails/active")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data is None


def test_get_prompt_count_by_type(authenticated_client, test_user):
    """Test GET /api/v1/custom-prompts/stats/count-by-type."""
    # Create prompts of different types
    prompt_types_counts = [
        ("evaluation", 2),
        ("judge", 1),
        ("guardrails", 3)
    ]
    
    for prompt_type, count in prompt_types_counts:
        for i in range(count):
            prompt_data = {
                "prompt_type": prompt_type,
                "name": f"{prompt_type} Prompt {i}",
                "content": f"Content for {prompt_type} {i}",
                "created_by_user_id": test_user["id"]
            }
            
            create_response = authenticated_client.post("/api/v1/custom-prompts", json=prompt_data)
            assert create_response.status_code == status.HTTP_201_CREATED
    
    # Get counts
    response = authenticated_client.get("/api/v1/custom-prompts/stats/count-by-type")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "counts" in data
    counts = data["counts"]
    assert counts["evaluation"] == 2
    assert counts["judge"] == 1
    assert counts["guardrails"] == 3


def test_get_custom_prompts_with_filters(authenticated_client, test_user):
    """Test GET /api/v1/custom-prompts with query parameters."""
    # Create prompts of different types and states
    prompts_data = [
        {"prompt_type": "evaluation", "name": "Active Evaluation", "is_active": True},
        {"prompt_type": "evaluation", "name": "Inactive Evaluation", "is_active": False},
        {"prompt_type": "judge", "name": "Active Judge", "is_active": True},
    ]
    
    for prompt_data in prompts_data:
        full_prompt_data = {
            **prompt_data,
            "content": f"Content for {prompt_data['name']}",
            "created_by_user_id": test_user["id"]
        }
        
        create_response = authenticated_client.post("/api/v1/custom-prompts", json=full_prompt_data)
        assert create_response.status_code == status.HTTP_201_CREATED
    
    # Test filtering by type
    response = authenticated_client.get("/api/v1/custom-prompts?prompt_type=evaluation")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["prompts"]) == 2
    for prompt in data["prompts"]:
        assert prompt["prompt_type"] == "evaluation"
    
    # Test filtering by active status
    response = authenticated_client.get("/api/v1/custom-prompts?active_only=true")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["prompts"]) == 2
    for prompt in data["prompts"]:
        assert prompt["is_active"] is True
    
    # Test pagination
    response = authenticated_client.get("/api/v1/custom-prompts?skip=1&limit=1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["prompts"]) == 1
    assert data["skip"] == 1
    assert data["limit"] == 1
