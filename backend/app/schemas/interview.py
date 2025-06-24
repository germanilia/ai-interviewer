from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, TYPE_CHECKING, List
from datetime import datetime
import secrets
import string
from app.models.interview import InterviewStatus, IntegrityScore, RiskLevel

if TYPE_CHECKING:
    from app.models.interview import Interview


def generate_pass_key() -> str:
    """Generate a unique 8-character alphanumeric pass key."""
    characters = string.ascii_uppercase + string.digits
    # Exclude confusing characters like 0, O, I, 1
    characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(characters) for _ in range(8))


class InterviewBase(BaseModel):
    """Base interview schema with common fields."""
    candidate_id: int
    job_id: int
    status: InterviewStatus = InterviewStatus.PENDING
    interview_date: Optional[datetime] = None


class InterviewCreate(InterviewBase):
    """Schema for creating a new interview."""
    pass_key: Optional[str] = None  # Will be auto-generated if not provided

    def model_post_init(self, __context: Any) -> None:
        """Auto-generate pass_key if not provided."""
        if self.pass_key is None:
            self.pass_key = generate_pass_key()

    def to_model(self) -> "Interview":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.interview import Interview
        return Interview(
            candidate_id=self.candidate_id,
            job_id=self.job_id,
            status=self.status,
            interview_date=self.interview_date,
            pass_key=self.pass_key
        )


class InterviewUpdate(BaseModel):
    """Schema for updating an interview."""
    job_id: Optional[int] = None
    status: Optional[InterviewStatus] = None
    interview_date: Optional[datetime] = None
    score: Optional[int] = None
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
    pass_key: str  # Required in response
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


class InterviewWithDetails(InterviewResponse):
    """Enhanced interview response with candidate and job details."""
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    job_title: Optional[str] = None
    job_department: Optional[str] = None

    @classmethod
    def from_model_with_details(cls, interview: "Interview") -> "InterviewWithDetails":
        """Convert SQLAlchemy model to Pydantic schema with related details."""
        instance = cls.model_validate(interview)

        # Add candidate details if available
        if hasattr(interview, 'candidate') and interview.candidate:
            instance.candidate_name = f"{interview.candidate.first_name} {interview.candidate.last_name}"
            instance.candidate_email = interview.candidate.email

        # Add job details if available
        if hasattr(interview, 'job') and interview.job:
            instance.job_title = interview.job.title
            instance.job_department = interview.job.department

        return instance


class InterviewListResponse(BaseModel):
    """Schema for paginated interview list responses."""
    items: List[InterviewWithDetails]
    total: int
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(ge=0, description="Total number of pages")
    status_counts: Optional[dict[str, int]] = None  # Count by status for tabs

    @classmethod
    def create(
        cls,
        items: List[InterviewWithDetails],
        total: int,
        page: int,
        page_size: int,
        status_counts: Optional[dict[str, int]] = None
    ) -> "InterviewListResponse":
        """Create paginated response."""
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            status_counts=status_counts or {}
        )
