from enum import Enum
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Union, cast
import json
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
from pydantic import BaseModel, Field

T = TypeVar('T', bound=BaseModel)

class ModelFamily(str, Enum):
    CLAUDE = "claude"
    LLAMA = "llama"
    NOVA = "nova"

class ModelName(str, Enum):
    # Claude models
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_7_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    
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
    max_tokens: int = 512
    temperature: float = 0.5
    top_p: float = 0.9
    reasoning: Optional[ReasoningConfig] = None

class LLMResponse(BaseModel):
    text: str
    reasoning_text: Optional[str] = None

class LLMClient(Generic[T]):
    def __init__(
        self,
        model_id: ModelName,
        region_name: str = "us-east-1",
        config: Optional[LLMConfig] = None
    ):
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for AWS Bedrock integration. Please install it with 'pip install boto3'.")
            
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region_name)
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
                return response["output"]["message"]["content"][0]["text"]
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
    
    def generate(self, message: str, response_model: Type[T]) -> T:
        """Generate a response for a single message"""
        try:
            request = self._prepare_native_api_request(message)
            json_request = json.dumps(request)
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json_request
            )
            
            model_response = json.loads(response["body"].read())
            response_text = self._extract_response_text(model_response)
            
            # Parse the response into the provided Pydantic model
            return response_model.model_validate({"text": response_text})
            
        except Exception as e:
            raise Exception(f"Error invoking model '{self.model_id}': {e}")
    
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
        region_name: str = "us-east-1",
        config: Optional[LLMConfig] = None
    ) -> LLMClient:
        return LLMClient(
            model_id=model_name,
            region_name=region_name,
            config=config
        )

# Example usage:
# from backend.app.core.llm_service import LLMFactory, ModelName, LLMConfig, ReasoningConfig, LLMResponse
# 
# # Create a client with default settings
# client = LLMFactory.create_client(ModelName.CLAUDE_3_HAIKU)
# 
# # Create a client with custom settings
# config = LLMConfig(
#     max_tokens=1024,
#     temperature=0.7,
#     top_p=0.95,
#     reasoning=ReasoningConfig(enabled=True, budget_tokens=1000)
# )
# client_with_config = LLMFactory.create_client(
#     model_name=ModelName.CLAUDE_3_7_SONNET,
#     region_name="us-west-2",
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
