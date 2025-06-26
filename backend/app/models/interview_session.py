from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from enum import StrEnum


class InterviewSessionStatus(StrEnum):
    """Interview session status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class InterviewSession(Base):
    """
    SQLAlchemy InterviewSession model for tracking individual candidate interview sessions
    """
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    
    # Session state
    status = Column(Enum(InterviewSessionStatus), default=InterviewSessionStatus.ACTIVE, nullable=False)
    current_question_index = Column(Integer, default=0, nullable=False)  # 0-based index of current question

    # Conversation data - stored as JSON array of messages
    # Format: [{"role": "assistant|user", "content": "message", "timestamp": "ISO datetime", "question_id": int|null}]
    conversation_history = Column(JSON, default=list, nullable=False)
    
    # Session metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Session statistics for reporting
    total_messages = Column(Integer, default=0, nullable=False)
    questions_asked = Column(Integer, default=0, nullable=False)
    session_duration_minutes = Column(Integer, nullable=True)  # Calculated when session ends
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interview_sessions")
    interview = relationship("Interview")
