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
    SQLAlchemy Interview model for integrity interviews
    """
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    # Interview basic info
    status = Column(Enum(InterviewStatus), default=InterviewStatus.PENDING, nullable=False)
    interview_date = Column(DateTime(timezone=True), nullable=True)
    pass_key = Column(String(12), unique=True, nullable=False, index=True)
    
    # Interview results
    score = Column(Integer, nullable=True)  # Numeric score 0-100
    integrity_score = Column(Enum(IntegrityScore), nullable=True)
    risk_level = Column(Enum(RiskLevel), nullable=True)
    
    # Conversation and analysis
    conversation = Column(JSON, nullable=True)  # Full conversation in JSON format
    
    # Report fields (integrated based on documentation)
    report_summary = Column(Text, nullable=True)  # Applicant profile overview
    risk_indicators = Column(JSON, nullable=True)  # Array of identified red flags
    key_concerns = Column(JSON, nullable=True)  # Areas requiring further investigation
    analysis_notes = Column(Text, nullable=True)  # Additional analysis notes
    
    # Metadata
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    created_by = relationship("User", back_populates="created_interviews")
    candidate = relationship("Candidate", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
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
    job_questions = relationship("JobQuestion", back_populates="question")


class Job(Base):
    """Job positions that candidates interview for"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    department = Column(String, nullable=True)

    # Metadata
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="created_jobs")
    job_questions = relationship("JobQuestion", back_populates="job", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="job")


class JobQuestion(Base):
    """Questions template for a specific job position"""
    __tablename__ = "job_questions"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    order_index = Column(Integer, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="job_questions")
    question = relationship("Question", back_populates="job_questions")


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
