"""
Unit tests for Interview schemas to verify validation and model conversion.
"""
import pytest
from datetime import datetime
from app.schemas.interview import InterviewCreate, InterviewResponse, InterviewWithDetails
from app.models.interview import Interview, InterviewStatus
from app.models.candidate import Candidate


def test_interview_create_success():
    """Test successful creation of InterviewCreate schema."""
    interview_data = {
        "job_title": "Software Engineer",
        "job_description": "Develop and maintain web applications.",
        "job_department": "Engineering",
        "instructions": "Please answer all questions to the best of your ability.",
        "question_ids": [1, 2, 3]
    }
    interview_create = InterviewCreate(**interview_data)
    assert interview_create.job_title == interview_data["job_title"]
    assert interview_create.question_ids == interview_data["question_ids"]


def test_interview_create_empty_questions_fails():
    """Test that InterviewCreate fails with an empty question_ids list."""
    with pytest.raises(ValueError):
        InterviewCreate(
            job_title="Software Engineer",
            question_ids=[]
        )


def test_interview_create_duplicate_questions_fails():
    """Test that InterviewCreate fails with duplicate question IDs."""
    with pytest.raises(ValueError):
        InterviewCreate(
            job_title="Software Engineer",
            question_ids=[1, 2, 2]
        )


def test_interview_create_to_model():
    """Test the conversion from InterviewCreate schema to Interview model."""
    interview_create = InterviewCreate(
        job_title="Software Engineer",
        job_description="Backend developer",
        question_ids=[1, 2]
    )
    user_id = 1
    interview_model = interview_create.to_model(created_by_user_id=user_id)

    assert isinstance(interview_model, Interview)
    assert getattr(interview_model, "job_title") == "Software Engineer"
    assert getattr(interview_model, "job_description") == "Backend developer"
    assert getattr(interview_model, "created_by_user_id") == user_id


def test_interview_response_from_model():
    """Test the conversion from Interview model to InterviewResponse schema."""
    now = datetime.utcnow()
    interview_model = Interview(
        id=1,
        job_title="Product Manager",
        total_candidates=5,
        completed_candidates=2,
        avg_score=85,
        created_at=now,
        updated_at=now
    )
    interview_response = InterviewResponse.from_model(interview_model)

    assert interview_response.id == 1
    assert interview_response.job_title == "Product Manager"
    assert interview_response.total_candidates == 5
    assert interview_response.completed_candidates == 2
    assert interview_response.avg_score == 85
    assert interview_response.created_at == now


def test_interview_with_details_from_model():
    """Test conversion to InterviewWithDetails, including candidate list."""
    now = datetime.utcnow()
    interview_model = Interview(
        id=1,
        job_title="UX Designer",
        created_at=now,
        updated_at=now,
        candidates=[
            Candidate(id=1, first_name="John", last_name="Doe", email="john.doe@example.com"),
            Candidate(id=2, first_name="Jane", last_name="Smith", email="jane.smith@example.com")
        ]
    )

    interview_details = InterviewWithDetails.from_model_with_details(interview_model)

    assert interview_details.id == 1
    assert interview_details.job_title == "UX Designer"
    assert interview_details.candidates_count == 2
    assert interview_details.assigned_candidates is not None
    assert len(interview_details.assigned_candidates) == 2
    assert interview_details.assigned_candidates[0]["name"] == "John Doe"
