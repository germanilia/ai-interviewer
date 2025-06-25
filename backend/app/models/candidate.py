from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base


class Candidate(Base):
    """
    SQLAlchemy Candidate model for job applicants
    """
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)

    # Interview assignment - candidates are assigned to interviews
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=True)
    pass_key = Column(String(12), unique=True, nullable=True, index=True)  # Unique key for interview access

    # Interview-specific data for this candidate
    interview_status = Column(String, nullable=True)  # Will use string for now, can be enum later
    interview_date = Column(DateTime(timezone=True), nullable=True)
    score = Column(Integer, nullable=True)  # Numeric score 0-100
    integrity_score = Column(String, nullable=True)  # Will use string for now, can be enum later
    risk_level = Column(String, nullable=True)  # Will use string for now, can be enum later

    # Conversation and analysis for this candidate
    conversation = Column(JSON, nullable=True)  # Full conversation in JSON format
    report_summary = Column(Text, nullable=True)  # Applicant profile overview
    risk_indicators = Column(JSON, nullable=True)  # Array of identified red flags
    key_concerns = Column(JSON, nullable=True)  # Areas requiring further investigation
    analysis_notes = Column(Text, nullable=True)  # Additional analysis notes
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="created_candidates")
    interview = relationship("Interview", back_populates="candidates")
