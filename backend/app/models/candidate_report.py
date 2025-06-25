from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from enum import StrEnum


class ReportGrade(StrEnum):
    """Report final grade enum"""
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    POOR = "poor"
    FAIL = "fail"


class RiskLevel(StrEnum):
    """Risk level enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CandidateReport(Base):
    """
    SQLAlchemy CandidateReport model for storing AI-generated candidate assessment reports
    """
    __tablename__ = "candidate_reports"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to candidate
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, unique=True)
    
    # Report content
    header = Column(String, nullable=False)  # Report header/title
    risk_factors = Column(JSON, nullable=False, default=list)  # List of risk factor objects
    overall_risk_level = Column(String, nullable=False)  # Overall risk assessment
    general_observation = Column(Text, nullable=False)  # General observations
    final_grade = Column(String, nullable=False)  # Final grade
    general_impression = Column(Text, nullable=False)  # General impression and recommendation
    
    # Additional metadata
    confidence_score = Column(Float, nullable=True)  # AI confidence in assessment (0-1)
    key_strengths = Column(JSON, nullable=False, default=list)  # List of key strengths
    areas_of_concern = Column(JSON, nullable=False, default=list)  # List of areas of concern
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="report")
