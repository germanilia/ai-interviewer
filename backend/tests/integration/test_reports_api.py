"""
Integration tests for Reports API endpoints.
Tests the complete flow from HTTP request to database operations.
"""
import pytest
from fastapi import status
from app.schemas.reports import ReportGenerationRequest, ReportType, ReportFormat


def test_get_overview_endpoint_requires_auth(client):
    """Test that GET /api/v1/reports/overview requires authentication."""
    response = client.get("/api/v1/reports/overview")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_analytics_endpoint_requires_auth(client):
    """Test that GET /api/v1/reports/analytics requires authentication."""
    response = client.get("/api/v1/reports/analytics")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_generate_report_endpoint_requires_auth(client):
    """Test that POST /api/v1/reports/generate requires authentication."""
    report_data = {
        "report_type": "candidate",
        "format": "pdf",
        "candidate_id": 1
    }
    response = client.post("/api/v1/reports/generate", json=report_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_available_fields_endpoint_requires_auth(client):
    """Test that GET /api/v1/reports/fields/{data_source} requires authentication."""
    response = client.get("/api/v1/reports/fields/interviews")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_custom_report_endpoint_requires_auth(client):
    """Test that POST /api/v1/reports/custom requires authentication."""
    custom_report_data = {
        "definition": {
            "name": "Test Report",
            "data_source": "interviews",
            "selected_fields": []
        },
        "format": "csv"
    }
    response = client.post("/api/v1/reports/custom", json=custom_report_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_report_history_endpoint_requires_auth(client):
    """Test that GET /api/v1/reports/history requires authentication."""
    response = client.get("/api/v1/reports/history")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_export_report_endpoint_requires_auth(client):
    """Test that POST /api/v1/reports/export requires authentication."""
    export_data = {
        "report_id": 1,
        "format": "excel"
    }
    response = client.post("/api/v1/reports/export", json=export_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_download_report_endpoint_requires_auth(client):
    """Test that GET /api/v1/reports/download/{report_id} requires authentication."""
    response = client.get("/api/v1/reports/download/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_report_endpoint_requires_auth(client):
    """Test that DELETE /api/v1/reports/{report_id} requires authentication."""
    response = client.delete("/api/v1/reports/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_schedule_report_endpoint_requires_auth(client):
    """Test that POST /api/v1/reports/schedule requires authentication."""
    schedule_data = {
        "report_type": "analytics",
        "frequency": "weekly",
        "schedule_time": "09:00",
        "recipients": ["admin@test.com"]
    }
    response = client.post("/api/v1/reports/schedule", json=schedule_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_chart_data_endpoint_requires_auth(client):
    """Test that GET /api/v1/reports/charts/{chart_type} requires authentication."""
    response = client.get("/api/v1/reports/charts/interview-volume")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_overview_data_authenticated(authenticated_client, sample_data):
    """Test getting overview data with authentication."""
    response = authenticated_client.get("/api/v1/reports/overview")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    assert "summary_cards" in data["data"]
    assert "trends_chart" in data["data"]
    assert "risk_distribution_chart" in data["data"]
    assert "department_breakdown_chart" in data["data"]
    assert "recent_interviews" in data["data"]


def test_get_overview_data_with_filters(authenticated_client, sample_data):
    """Test getting overview data with filters."""
    response = authenticated_client.get(
        "/api/v1/reports/overview",
        params={
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
            "department": "Engineering"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "filters_applied" in data
    if data["filters_applied"]:
        assert data["filters_applied"]["department"] == "Engineering"


def test_get_analytics_data_authenticated(authenticated_client, sample_data):
    """Test getting analytics data with authentication."""
    response = authenticated_client.get("/api/v1/reports/analytics")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "data" in data
    assert "interview_volume_chart" in data["data"]
    assert "risk_trends_chart" in data["data"]
    assert "completion_rates_chart" in data["data"]
    assert "score_distribution_chart" in data["data"]
    assert "department_comparison_chart" in data["data"]
    assert "time_to_complete_chart" in data["data"]


def test_generate_candidate_report_authenticated(authenticated_client, sample_data):
    """Test generating candidate report with authentication."""
    report_data = {
        "report_type": "candidate",
        "format": "pdf",
        "candidate_id": 1
    }
    
    response = authenticated_client.post("/api/v1/reports/generate", json=report_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "report_id" in data
    assert "download_url" in data
    assert "metadata" in data


def test_generate_interview_report_authenticated(authenticated_client, sample_data):
    """Test generating interview report with authentication."""
    report_data = {
        "report_type": "interview",
        "format": "excel",
        "interview_id": 1
    }
    
    response = authenticated_client.post("/api/v1/reports/generate", json=report_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "report_id" in data
    assert "download_url" in data


def test_generate_analytics_report_authenticated(authenticated_client, sample_data):
    """Test generating analytics report with authentication."""
    report_data = {
        "report_type": "analytics",
        "format": "pdf"
    }
    
    response = authenticated_client.post("/api/v1/reports/generate", json=report_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "report_id" in data


def test_get_available_fields_interviews(authenticated_client):
    """Test getting available fields for interviews."""
    response = authenticated_client.get("/api/v1/reports/fields/interviews")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["data_source"] == "interviews"
    assert "fields" in data
    assert len(data["fields"]) > 0
    
    # Check for expected fields
    field_names = [field["field_name"] for field in data["fields"]]
    assert "id" in field_names
    assert "status" in field_names
    assert "score" in field_names


def test_get_available_fields_candidates(authenticated_client):
    """Test getting available fields for candidates."""
    response = authenticated_client.get("/api/v1/reports/fields/candidates")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["data_source"] == "candidates"
    assert "fields" in data
    assert len(data["fields"]) > 0


def test_get_available_fields_jobs(authenticated_client):
    """Test getting available fields for jobs."""
    response = authenticated_client.get("/api/v1/reports/fields/jobs")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["data_source"] == "jobs"
    assert "fields" in data
    assert len(data["fields"]) > 0


def test_get_available_fields_invalid_source(authenticated_client):
    """Test getting available fields for invalid data source."""
    response = authenticated_client.get("/api/v1/reports/fields/invalid")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_custom_report_authenticated(authenticated_client):
    """Test creating custom report with authentication."""
    custom_report_data = {
        "definition": {
            "name": "Test Custom Report",
            "description": "A test report",
            "data_source": "interviews",
            "selected_fields": [
                {
                    "field_name": "id",
                    "display_name": "Interview ID",
                    "field_type": "number",
                    "is_required": False
                }
            ]
        },
        "format": "csv",
        "save_definition": False
    }
    
    response = authenticated_client.post("/api/v1/reports/custom", json=custom_report_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "report_id" in data


def test_get_report_history_authenticated(authenticated_client):
    """Test getting report history with authentication."""
    response = authenticated_client.get("/api/v1/reports/history")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "reports" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data


def test_get_report_history_with_pagination(authenticated_client):
    """Test getting report history with pagination."""
    response = authenticated_client.get(
        "/api/v1/reports/history",
        params={"page": 1, "page_size": 5}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["page"] == 1
    assert data["page_size"] == 5


def test_export_report_authenticated(authenticated_client):
    """Test exporting report with authentication."""
    export_data = {
        "report_id": 1,
        "format": "excel",
        "include_metadata": True
    }
    
    response = authenticated_client.post("/api/v1/reports/export", json=export_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "download_url" in data


def test_schedule_report_authenticated(authenticated_client):
    """Test scheduling report with authentication."""
    schedule_data = {
        "report_type": "analytics",
        "frequency": "weekly",
        "schedule_time": "09:00",
        "recipients": ["admin@test.com"],
        "format": "pdf",
        "is_enabled": True
    }
    
    response = authenticated_client.post("/api/v1/reports/schedule", json=schedule_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "message" in data
    assert "schedule_id" in data
    assert data["frequency"] == "weekly"


def test_get_chart_data_authenticated(authenticated_client, sample_data):
    """Test getting specific chart data with authentication."""
    response = authenticated_client.get("/api/v1/reports/charts/interview-volume")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["success"] is True
    assert "chart_data" in data
    assert data["chart_data"]["title"] == "Interview Volume (Last 30 Days)"


def test_get_chart_data_invalid_type(authenticated_client):
    """Test getting chart data with invalid chart type."""
    response = authenticated_client.get("/api/v1/reports/charts/invalid-chart")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
