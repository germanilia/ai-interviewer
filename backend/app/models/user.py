from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from app.db import Base
import enum


class UserRole(str, enum.Enum):
    """User roles enum"""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """
    SQLAlchemy User model
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, server_default=expression.true(), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    cognito_sub = Column(String, unique=True, index=True, nullable=True)  # Cognito user ID

    # Relationships
    created_questions = relationship("Question", back_populates="created_by")
    created_candidates = relationship("Candidate", back_populates="created_by")
    created_interviews = relationship("Interview", back_populates="created_by")
    created_custom_prompts = relationship("CustomPrompt", back_populates="created_by")
