from enum import Enum
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Union, cast
import json
import re
import logging
from pydantic import BaseModel

# Define boto3 at module level to ensure it's always defined
import boto3
from app.core.config_service import config_service

T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)

class ModelFamily(str, Enum):
    CLAUDE = "claude"
    LLAMA = "llama"
    NOVA = "nova"

class ModelName(str, Enum):
    # Claude models
    CLAUDE_3_5_HAIKU = "anthropic.claude-3-5-haiku-20241022-v1:0"
    CLAUDE_4_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    
    # Llama models
    LLAMA_3_8B = "meta.llama3-8b-instruct-v1:0"
    
    # Amazon Nova models
    NOVA_LITE = "amazon.nova-lite-v1:0"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ContentBlock(BaseModel):
    text: str

class Message(BaseModel):
    role: MessageRole
    content: List[ContentBlock]

class ReasoningConfig(BaseModel):
    enabled: bool = True
    budget_tokens: int = 2000

class LLMConfig(BaseModel):
    max_tokens: int = 8000
    temperature: float = 0.4
    top_p: float = 0.9
    reasoning: Optional[ReasoningConfig] = None

class LLMResponse(BaseModel):
    text: str
    reasoning_text: Optional[str] = None

class LLMClient(Generic[T]):
    def __init__(
        self,
        model_id: ModelName,
        config: Optional[LLMConfig] = None
    ):

        self.model_id = model_id

        # Get AWS credentials and region from config service
        aws_credentials = config_service.get_aws_credentials()

        # Create boto3 client with credentials from config service
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=aws_credentials["region"],
            aws_access_key_id=aws_credentials["access_key_id"],
            aws_secret_access_key=aws_credentials["secret_access_key"]
        )

        self.config = config or LLMConfig()
    
    def _get_model_family(self) -> ModelFamily:
        if "anthropic" in self.model_id:
            return ModelFamily.CLAUDE
        elif "meta" in self.model_id or "llama" in self.model_id:
            return ModelFamily.LLAMA
        elif "amazon" in self.model_id or "nova" in self.model_id:
            return ModelFamily.NOVA
        else:
            raise ValueError(f"Unsupported model: {self.model_id}")
    
    def _prepare_conversation_api_request(self, messages: List[Message]) -> Dict:
        return {
            "modelId": self.model_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": [{"text": content_block.text} for content_block in msg.content]
                }
                for msg in messages
            ],
            "inferenceConfig": {
                "maxTokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "topP": self.config.top_p
            }
        }
    
    def _prepare_native_api_request(self, message: str) -> Dict:
        family = self._get_model_family()
        
        if family == ModelFamily.CLAUDE:
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": message}],
                    }
                ],
            }
        
        # Similar implementations for other model families would go here
        raise ValueError(f"Native API not implemented for model family: {family}")
    
    def _extract_response_text(self, response: Dict) -> str:
        family = self._get_model_family()
        
        if family == ModelFamily.CLAUDE or family == ModelFamily.LLAMA or family == ModelFamily.NOVA:
            # For the Conversation API format
            try:
                return response["content"][0]["text"]
            except (KeyError, IndexError):
                pass
            
            # For the Native API format
            try:
                return response["content"][0]["text"]
            except (KeyError, IndexError):
                pass
        
        raise ValueError(f"Could not extract response text from: {response}")
    
    def _prepare_reasoning_config(self) -> Optional[Dict]:
        if not self.config.reasoning or not self.config.reasoning.enabled:
            return None
        
        return {
            "thinking": {
                "type": "enabled",
                "budget_tokens": self.config.reasoning.budget_tokens
            }
        }
    
    def _extract_reasoning_text(self, response: Dict) -> Optional[str]:
        try:
            for block in response["output"]["message"]["content"]:
                if block.get("reasoningContent"):
                    return block["reasoningContent"]["reasoningText"]
        except (KeyError, IndexError, TypeError):
            pass
        
        return None

    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON content between the outermost curly braces using regex"""
        # Pattern to match content between the first { and the last }
        pattern = r'\{.*\}'

        # Use DOTALL flag to match across newlines
        match = re.search(pattern, text, re.DOTALL)

        if match:
            return match.group(0)
        else:
            raise ValueError(f"No JSON content found in text: {text[:200]}...")

    def generate(self, message: str, response_model: Type[T], max_retries: int = 3) -> T:
        """Generate a response for a single message with retry logic"""
        original_message = message
        error_history = []

        for attempt in range(max_retries):
            try:
                # Add error history to the message for subsequent attempts
                current_message = original_message
                if error_history:
                    error_context = "\n\nPrevious errors to avoid:\n" + "\n".join(error_history)
                    current_message += error_context

                current_message += f"""

You are required to respond in the following JSON format:
{response_model.model_json_schema()}

the response must start with {{ and end with }}
"""

                request = self._prepare_native_api_request(current_message)
                json_request = json.dumps(request)

                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=json_request
                )

                model_response = json.loads(response["body"].read())
                response_text = self._extract_response_text(model_response)

                # Extract JSON from the response text
                json_content = self._extract_json_from_text(response_text)

                # Parse the JSON content into the provided Pydantic model
                parsed_json = json.loads(json_content)
                return response_model.model_validate(parsed_json)

            except (json.JSONDecodeError, ValueError) as e:
                error_msg = f"Attempt {attempt + 1}: JSON parsing error - {str(e)}"
                error_history.append(error_msg)
                logger.warning(error_msg)

                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate valid JSON after {max_retries} attempts. Last error: {e}")

            except Exception as e:
                error_msg = f"Attempt {attempt + 1}: General error - {str(e)}"
                error_history.append(error_msg)
                logger.warning(error_msg)

                if attempt == max_retries - 1:
                    raise Exception(f"Error invoking model '{self.model_id}' after {max_retries} attempts: {e}")

        # This should never be reached, but just in case
        raise Exception(f"Unexpected error: Failed to generate response after {max_retries} attempts")
    
    def converse(self, messages: List[Message], response_model: Type[T]) -> T:
        """Generate a response for a conversation"""
        try:
            request = self._prepare_conversation_api_request(messages)
            
            reasoning_config = self._prepare_reasoning_config()
            if reasoning_config:
                request["additionalModelRequestFields"] = reasoning_config
            
            response = self.client.converse(**request)
            
            response_text = self._extract_response_text(response)
            reasoning_text = self._extract_reasoning_text(response) if self.config.reasoning else None
            
            # Create a response dict based on the response_model fields
            response_dict: Dict[str, Any] = {"text": response_text}
            if reasoning_text is not None and "reasoning_text" in response_model.__annotations__:
                response_dict["reasoning_text"] = reasoning_text
            
            # Parse the response into the provided Pydantic model
            return response_model.model_validate(response_dict)
            
        except Exception as e:
            raise Exception(f"Error in conversation with model '{self.model_id}': {e}")

class LLMFactory:
    @staticmethod
    def create_client(
        model_name: ModelName,
        config: Optional[LLMConfig] = None
    ) -> LLMClient:
        return LLMClient(
            model_id=model_name,
            config=config
        )

# Example usage:
# from backend.app.core.llm_service import LLMFactory, ModelName, LLMConfig, ReasoningConfig, LLMResponse
#
# # Create a client with default settings
# client = LLMFactory.create_client(ModelName.CLAUDE_3_5_HAIKU)
#
# # Create a client with custom settings
# config = LLMConfig(
#     max_tokens=1024,
#     temperature=0.7,
#     top_p=0.95,
#     reasoning=ReasoningConfig(enabled=True, budget_tokens=1000)
# )
# client_with_config = LLMFactory.create_client(
#     model_name=ModelName.CLAUDE_4_SONNET,
#     config=config
# )
# 
# # Example custom response model
# class CustomResponse(BaseModel):
#     text: str
#     sentiment: Optional[str] = None
# 
# # Generate a response
# response = client.generate("Hello, how are you?", LLMResponse)
# print(response.text)
# 
# # Generate a response with a custom model
# custom_response = client.generate("How's the weather today?", CustomResponse)
# print(custom_response.text)
