from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from enum import StrEnum


class InterviewStatus(StrEnum):
    """Interview status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewLanguage(StrEnum):
    """Interview language enum"""
    HEBREW = "Hebrew"
    ENGLISH = "English"
    ARABIC = "Arabic"


class IntegrityScore(StrEnum):
    """Integrity score categories"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(StrEnum):
    """Risk level categories"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QuestionImportance(StrEnum):
    """Question importance levels"""
    OPTIONAL = "optional"           # Can be skipped, any answer accepted
    ASK_ONCE = "ask_once"          # Must be asked but any answer accepted
    MANDATORY = "mandatory"         # Must be asked and properly answered


class QuestionCategory(StrEnum):
    """Question categories for interview topics"""
    CRIMINAL_BACKGROUND = "criminal_background"
    DRUG_USE = "drug_use"
    ETHICS = "ethics"
    DISMISSALS = "dismissals"
    TRUSTWORTHINESS = "trustworthiness"
    GENERAL = "general"


class InterviewQuestionStatus(StrEnum):
    """Status of a question in an interview"""
    PENDING = "pending"
    ASKED = "asked"
    ANSWERED = "answered"
    SKIPPED = "skipped"


class Interview(Base):
    """
    SQLAlchemy Interview model for integrity interviews with job information
    """
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)

    # Job information (merged from Job model)
    job_title = Column(String, nullable=False)
    job_description = Column(Text, nullable=True)
    job_department = Column(String, nullable=True)

    # Interview language
    language = Column(Enum(InterviewLanguage), default=InterviewLanguage.HEBREW, nullable=False)

    # Initial greeting message for candidates
    initial_greeting = Column(Text, nullable=True)

    # General interview data (aggregated from candidates)
    avg_score = Column(Integer, nullable=True)  # Average score from all candidates
    total_candidates = Column(Integer, default=0, nullable=False)
    completed_candidates = Column(Integer, default=0, nullable=False)

    # General notes and instructions
    instructions = Column(Text, nullable=True)  # General interview instructions
    
    # Metadata
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    created_by = relationship("User", back_populates="created_interviews")
    candidates = relationship("Candidate", back_populates="interview")
    interview_questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan")


class Question(Base):
    """Question bank for interviews"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    instructions = Column(Text, nullable=True)
    importance = Column(Enum(QuestionImportance), nullable=False)
    category = Column(Enum(QuestionCategory), nullable=False)

    # Metadata
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="created_questions")
    interview_questions = relationship("InterviewQuestion", back_populates="question")


class InterviewQuestion(Base):
    """Questions assigned to a specific interview"""
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)

    # Question state in this interview
    status = Column(Enum(InterviewQuestionStatus), default=InterviewQuestionStatus.PENDING, nullable=False)
    order_index = Column(Integer, nullable=False)

    # Question and answer data for this interview
    question_text_snapshot = Column(Text, nullable=False)
    candidate_answer = Column(Text, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    follow_up_questions = Column(JSON, nullable=True)

    # Timestamps
    asked_at = Column(DateTime(timezone=True), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    interview = relationship("Interview", back_populates="interview_questions")
    question = relationship("Question", back_populates="interview_questions")
