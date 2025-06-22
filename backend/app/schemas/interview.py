from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, TYPE_CHECKING
from datetime import datetime
from app.models.interview import InterviewStatus, IntegrityScore, RiskLevel

if TYPE_CHECKING:
    from app.models.interview import Interview


class InterviewBase(BaseModel):
    """Base interview schema with common fields."""
    candidate_id: int
    job_id: int
    status: InterviewStatus = InterviewStatus.PENDING
    interview_date: Optional[datetime] = None


class InterviewCreate(InterviewBase):
    """Schema for creating a new interview."""

    def to_model(self) -> "Interview":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.interview import Interview
        return Interview(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            status=self.status,
            interview_date=self.interview_date
        )


class InterviewUpdate(BaseModel):
    """Schema for updating an interview."""
    job_id: Optional[int] = None
    status: Optional[InterviewStatus] = None
    interview_date: Optional[datetime] = None
    score: Optional[int] = Field(None, ge=0, le=100)
    integrity_score: Optional[IntegrityScore] = None
    risk_level: Optional[RiskLevel] = None
    conversation: Optional[dict[str, Any]] = None
    report_summary: Optional[str] = None
    risk_indicators: Optional[list[dict[str, Any]]] = None
    key_concerns: Optional[list[dict[str, Any]]] = None
    analysis_notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class InterviewResponse(InterviewBase):
    """Schema for interview responses."""
    id: int
    score: Optional[int] = None
    integrity_score: Optional[IntegrityScore] = None
    risk_level: Optional[RiskLevel] = None
    conversation: Optional[dict[str, Any]] = None
    report_summary: Optional[str] = None
    risk_indicators: Optional[list[dict[str, Any]]] = None
    key_concerns: Optional[list[dict[str, Any]]] = None
    analysis_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, interview: "Interview") -> "InterviewResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(interview)





class InterviewInDB(InterviewResponse):
    """Schema for interview data as stored in database."""

    @classmethod
    def from_model(cls, interview: "Interview") -> "InterviewInDB":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(interview)


class InterviewReport(BaseModel):
    """Schema for interview report generation."""
    interview_id: int
    candidate_name: str
    candidate_email: str
    job_title: str
    job_department: Optional[str]
    interview_date: Optional[datetime]
    status: InterviewStatus
    score: Optional[int]
    integrity_score: Optional[IntegrityScore]
    risk_level: Optional[RiskLevel]
    report_summary: Optional[str]
    risk_indicators: Optional[list[dict[str, Any]]]
    key_concerns: Optional[list[dict[str, Any]]]
    analysis_notes: Optional[str]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
