"""
Unit tests for LLM JSON extraction functionality.
"""
import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel
from app.core.llm_service import LLMClient, ModelName, LLMConfig


class TestResponse(BaseModel):
    """Test response model for JSON extraction tests"""
    message: str
    status: str


class TestLLMJSONExtraction:
    """Test cases for JSON extraction and retry logic"""

    def setup_method(self):
        """Set up test fixtures"""
        self.llm_client = LLMClient(ModelName.CLAUDE_3_5_HAIKU)

    def test_extract_json_from_text_success(self):
        """Test successful JSON extraction from text"""
        text_with_json = 'Here is the response: {"message": "Hello", "status": "success"} and some more text'
        
        result = self.llm_client._extract_json_from_text(text_with_json)
        
        assert result == '{"message": "Hello", "status": "success"}'

    def test_extract_json_from_text_multiline(self):
        """Test JSON extraction from multiline text"""
        text_with_json = '''Here is the response:
        {
            "message": "Hello world",
            "status": "success"
        }
        And some more text after'''
        
        result = self.llm_client._extract_json_from_text(text_with_json)
        
        expected = '''{
            "message": "Hello world",
            "status": "success"
        }'''
        assert result == expected

    def test_extract_json_from_text_no_json(self):
        """Test JSON extraction when no JSON is present"""
        text_without_json = "This is just plain text without any JSON content"
        
        with pytest.raises(ValueError, match="No JSON content found in text"):
            self.llm_client._extract_json_from_text(text_without_json)

    def test_extract_json_from_text_nested_braces(self):
        """Test JSON extraction with nested objects"""
        text_with_nested = 'Response: {"message": "Hello", "data": {"nested": "value"}, "status": "ok"}'
        
        result = self.llm_client._extract_json_from_text(text_with_nested)
        
        assert result == '{"message": "Hello", "data": {"nested": "value"}, "status": "ok"}'

    @patch('app.core.llm_service.boto3.client')
    def test_generate_success_first_attempt(self, mock_boto_client):
        """Test successful generation on first attempt"""
        # Mock the boto3 client and response
        mock_client_instance = Mock()
        mock_boto_client.return_value = mock_client_instance
        
        # Mock the response from the model
        mock_response = {
            "body": Mock()
        }
        mock_response["body"].read.return_value = '{"content": [{"text": "{\\"message\\": \\"Hello\\", \\"status\\": \\"success\\"}"}]}'
        mock_client_instance.invoke_model.return_value = mock_response
        
        # Create a new client instance to use the mocked boto3 client
        client = LLMClient(ModelName.CLAUDE_3_5_HAIKU)
        
        result = client.generate("Test message", TestResponse)
        
        assert isinstance(result, TestResponse)
        assert result.message == "Hello"
        assert result.status == "success"

    @patch('app.core.llm_service.boto3.client')
    def test_generate_retry_on_json_error(self, mock_boto_client):
        """Test retry logic when JSON parsing fails initially"""
        # Mock the boto3 client and response
        mock_client_instance = Mock()
        mock_boto_client.return_value = mock_client_instance
        
        # First call returns invalid JSON, second call returns valid JSON
        mock_response_1 = {
            "body": Mock()
        }
        mock_response_1["body"].read.return_value = '{"content": [{"text": "Invalid JSON response"}]}'
        
        mock_response_2 = {
            "body": Mock()
        }
        mock_response_2["body"].read.return_value = '{"content": [{"text": "{\\"message\\": \\"Hello\\", \\"status\\": \\"success\\"}"}]}'
        
        mock_client_instance.invoke_model.side_effect = [mock_response_1, mock_response_2]
        
        # Create a new client instance to use the mocked boto3 client
        client = LLMClient(ModelName.CLAUDE_3_5_HAIKU)
        
        result = client.generate("Test message", TestResponse)
        
        assert isinstance(result, TestResponse)
        assert result.message == "Hello"
        assert result.status == "success"
        assert mock_client_instance.invoke_model.call_count == 2

    @patch('app.core.llm_service.boto3.client')
    def test_generate_max_retries_exceeded(self, mock_boto_client):
        """Test that exception is raised when max retries are exceeded"""
        # Mock the boto3 client and response
        mock_client_instance = Mock()
        mock_boto_client.return_value = mock_client_instance
        
        # All calls return invalid JSON
        mock_response = {
            "body": Mock()
        }
        mock_response["body"].read.return_value = '{"content": [{"text": "Invalid JSON response"}]}'
        mock_client_instance.invoke_model.return_value = mock_response
        
        # Create a new client instance to use the mocked boto3 client
        client = LLMClient(ModelName.CLAUDE_3_5_HAIKU)
        
        with pytest.raises(Exception, match="Failed to generate valid JSON after 3 attempts"):
            client.generate("Test message", TestResponse, max_retries=3)
        
        assert mock_client_instance.invoke_model.call_count == 3
