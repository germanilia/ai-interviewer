"""
Unit tests for Interview schemas to verify pass_key functionality and validation.
"""
import pytest
from app.schemas.interview import InterviewCreate, InterviewResponse, generate_pass_key
from app.models.interview import InterviewStatus


def test_generate_pass_key_format():
    """Test that generate_pass_key creates properly formatted keys."""
    pass_key = generate_pass_key()
    
    # Should be 8 characters
    assert len(pass_key) == 8
    
    # Should be alphanumeric uppercase
    assert pass_key.isalnum()
    assert pass_key.isupper()
    
    # Should not contain confusing characters
    assert '0' not in pass_key
    assert 'O' not in pass_key
    assert 'I' not in pass_key
    assert '1' not in pass_key


def test_generate_pass_key_uniqueness():
    """Test that generate_pass_key creates unique keys."""
    keys = set()
    for _ in range(100):
        key = generate_pass_key()
        keys.add(key)
    
    # All keys should be unique
    assert len(keys) == 100


def test_interview_create_auto_generates_pass_key():
    """Test that InterviewCreate automatically generates pass_key."""
    interview_create = InterviewCreate(
        candidate_id=1,
        job_id=1,
        status=InterviewStatus.PENDING
    )
    
    # Pass key should be auto-generated
    assert interview_create.pass_key is not None
    assert len(interview_create.pass_key) == 8
    assert interview_create.pass_key.isalnum()


def test_interview_create_preserves_custom_pass_key():
    """Test that InterviewCreate preserves custom pass_key when provided."""
    custom_key = "CUSTOM12"
    interview_create = InterviewCreate(
        candidate_id=1,
        job_id=1,
        status=InterviewStatus.PENDING,
        pass_key=custom_key
    )
    
    # Custom pass key should be preserved
    assert interview_create.pass_key == custom_key


def test_interview_create_to_model_includes_pass_key():
    """Test that to_model() includes the pass_key."""
    interview_create = InterviewCreate(
        candidate_id=1,
        job_id=1,
        status=InterviewStatus.PENDING
    )
    
    # Convert to model
    interview_model = interview_create.to_model()
    
    # Model should have the pass_key
    assert interview_model.pass_key == interview_create.pass_key
    assert interview_model.candidate_id == 1
    assert interview_model.job_id == 1
    assert interview_model.status == InterviewStatus.PENDING


def test_interview_response_requires_pass_key():
    """Test that InterviewResponse requires pass_key field."""
    # This should work with pass_key
    interview_response = InterviewResponse(
        id=1,
        candidate_id=1,
        job_id=1,
        status=InterviewStatus.PENDING,
        pass_key="TESTKEY1",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z"
    )
    
    assert interview_response.pass_key == "TESTKEY1"
    assert interview_response.id == 1


def test_multiple_interview_creates_have_unique_pass_keys():
    """Test that multiple InterviewCreate instances get unique pass_keys."""
    interviews = []
    for i in range(10):
        interview = InterviewCreate(
            candidate_id=i + 1,
            job_id=1,
            status=InterviewStatus.PENDING
        )
        interviews.append(interview)
    
    # All pass_keys should be unique
    pass_keys = [interview.pass_key for interview in interviews]
    assert len(set(pass_keys)) == 10
