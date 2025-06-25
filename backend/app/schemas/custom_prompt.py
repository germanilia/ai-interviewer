"""
Custom prompt schemas for API requests and responses.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.custom_prompt import PromptType


class CustomPromptBase(BaseModel):
    """Base custom prompt schema"""
    prompt_type: PromptType
    name: str
    content: str
    description: Optional[str] = None
    is_active: bool = True


class CustomPromptCreate(CustomPromptBase):
    """Schema for creating a new custom prompt"""
    created_by_user_id: int


class CustomPromptUpdate(BaseModel):
    """Schema for updating a custom prompt"""
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CustomPromptResponse(CustomPromptBase):
    """Complete custom prompt response schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, prompt) -> Optional["CustomPromptResponse"]:
        """Convert from SQLAlchemy model to Pydantic schema"""
        if not prompt:
            return None
        
        return cls(
            id=prompt.id,
            prompt_type=prompt.prompt_type,
            name=prompt.name,
            content=prompt.content,
            description=prompt.description,
            is_active=prompt.is_active,
            created_by_user_id=prompt.created_by_user_id,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at
        )


class CustomPromptInDB(CustomPromptResponse):
    """Custom prompt schema for internal database operations"""
    pass


class CustomPromptListResponse(BaseModel):
    """Response schema for listing custom prompts"""
    prompts: list[CustomPromptResponse]
    total: int
    skip: int
    limit: int
