from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import StrEnum
from app.db import Base


class PromptType(StrEnum):
    """Enum for different types of prompts"""
    EVALUATION = "EVALUATION"
    JUDGE = "JUDGE"
    GUARDRAILS = "GUARDRAILS"
    QUESTION_EVALUATION = "QUESTION_EVALUATION"


class CustomPrompt(Base):
    """
    SQLAlchemy CustomPrompt model for storing custom prompts
    """
    __tablename__ = "custom_prompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt_type = Column(SQLEnum(PromptType), nullable=False, index=True)
    name = Column(String, nullable=False)  # Human-readable name for the prompt
    content = Column(Text, nullable=False)  # The actual prompt content
    description = Column(Text, nullable=True)  # Optional description of what this prompt does
    is_active = Column(Boolean, default=True, nullable=False)  # Whether this prompt is currently active
    
    # Metadata
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="created_custom_prompts")
