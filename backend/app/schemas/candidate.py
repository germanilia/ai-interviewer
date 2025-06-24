from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class CandidateBase(BaseModel):
    """Base candidate schema with common fields."""
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema for creating a new candidate."""

    def to_model(self, created_by_user_id: int) -> "Candidate":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.candidate import Candidate
        return Candidate(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone=self.phone,
            created_by_user_id=created_by_user_id
        )


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class CandidateResponse(CandidateBase):
    """Schema for candidate responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    # Additional computed fields for UI
    full_name: Optional[str] = None
    interview_count: Optional[int] = None
    last_interview_date: Optional[datetime] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, candidate: "Candidate") -> "CandidateResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        instance = cls.model_validate(candidate)
        # Compute full name
        instance.full_name = f"{candidate.first_name} {candidate.last_name}"
        # Compute interview stats (will be populated by service layer)
        instance.interview_count = len(candidate.interviews) if hasattr(candidate, 'interviews') and candidate.interviews else 0
        instance.last_interview_date = (
            max(interview.created_at for interview in candidate.interviews)
            if hasattr(candidate, 'interviews') and candidate.interviews
            else None
        )
        # Determine status based on interviews
        if hasattr(candidate, 'interviews') and candidate.interviews:
            recent_interviews = [i for i in candidate.interviews if hasattr(i, 'status')]
            if any(i.status == 'in_progress' for i in recent_interviews):
                instance.status = 'active'
            elif any(i.status == 'completed' for i in recent_interviews):
                instance.status = 'completed'
            else:
                instance.status = 'pending'
        else:
            instance.status = 'new'
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
    page_size: int = Field(ge=1, le=100, description="Number of items per page")
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
