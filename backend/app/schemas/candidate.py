from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, TYPE_CHECKING, List, Any
from datetime import datetime
import secrets
import string

if TYPE_CHECKING:
    from app.models.candidate import Candidate


def generate_pass_key() -> str:
    """Generate a unique 8-character alphanumeric pass key."""
    characters = string.ascii_uppercase + string.digits
    # Exclude confusing characters like 0, O, I, 1
    characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(characters) for _ in range(8))


class CandidateBase(BaseModel):
    """Base candidate schema with common fields."""
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema for creating a new candidate with interview assignment."""
    interview_id: Optional[int] = Field(None, description="Interview ID to assign candidate to")
    pass_key: Optional[str] = Field(None, description="Pass key for interview access (auto-generated if not provided)")

    def model_post_init(self, __context: Any) -> None:
        """Auto-generate pass_key if not provided and interview is assigned."""
        if self.interview_id and self.pass_key is None:
            self.pass_key = generate_pass_key()

    def to_model(self, created_by_user_id: int) -> "Candidate":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.candidate import Candidate
        return Candidate(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone=self.phone,
            interview_id=self.interview_id,
            pass_key=self.pass_key,
            created_by_user_id=created_by_user_id
        )


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate."""
    # Basic candidate info
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    # Interview assignment
    interview_id: Optional[int] = None
    pass_key: Optional[str] = None

    # Interview-specific data for this candidate
    interview_status: Optional[str] = None
    interview_date: Optional[datetime] = None
    score: Optional[int] = None
    integrity_score: Optional[str] = None
    risk_level: Optional[str] = None
    conversation: Optional[dict[str, Any]] = None
    report_summary: Optional[str] = None
    risk_indicators: Optional[list[dict[str, Any]]] = None
    key_concerns: Optional[list[dict[str, Any]]] = None
    analysis_notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class CandidateResponse(CandidateBase):
    """Schema for candidate responses."""
    id: int

    # Interview assignment
    interview_id: Optional[int] = None
    pass_key: Optional[str] = None

    # Interview-specific data for this candidate
    interview_status: Optional[str] = None
    interview_date: Optional[datetime] = None
    score: Optional[int] = None
    integrity_score: Optional[str] = None
    risk_level: Optional[str] = None
    conversation: Optional[dict[str, Any]] = None
    report_summary: Optional[str] = None
    risk_indicators: Optional[list[dict[str, Any]]] = None
    key_concerns: Optional[list[dict[str, Any]]] = None
    analysis_notes: Optional[str] = None
    completed_at: Optional[datetime] = None

    # Metadata
    created_at: datetime
    updated_at: datetime

    # Additional computed fields for UI
    full_name: Optional[str] = None
    interview_title: Optional[str] = None  # Job title from assigned interview

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, candidate: "Candidate") -> "CandidateResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        instance = cls.model_validate(candidate)
        # Compute full name
        instance.full_name = f"{candidate.first_name} {candidate.last_name}"

        # Add interview title if assigned to an interview
        if hasattr(candidate, 'interview') and candidate.interview:
            instance.interview_title = candidate.interview.job_title

        return instance


class CandidateInDB(CandidateResponse):
    """Schema for candidate data as stored in database."""

    @classmethod
    def from_model(cls, candidate: "Candidate") -> "CandidateInDB":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(candidate)


class CandidateListResponse(BaseModel):
    """Schema for paginated candidate list responses."""
    items: List[CandidateResponse]
    total: int
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=1000, description="Number of items per page")
    total_pages: int = Field(ge=0, description="Total number of pages")

    @classmethod
    def create(cls, items: List[CandidateResponse], total: int, page: int, page_size: int) -> "CandidateListResponse":
        """Create paginated response."""
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
