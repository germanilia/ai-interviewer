from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, TYPE_CHECKING
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

    def to_model(self) -> "Candidate":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.candidate import Candidate
        return Candidate(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone=self.phone
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

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, candidate: "Candidate") -> "CandidateResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(candidate)


class CandidateWithInterviews(CandidateResponse):
    """Schema for candidate with interviews included."""
    from app.schemas.interview import InterviewResponse
    interviews: list[InterviewResponse] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, candidate: "Candidate") -> "CandidateWithInterviews":
        """Convert SQLAlchemy model to Pydantic schema with interviews."""
        return cls.model_validate(candidate)


class CandidateInDB(CandidateResponse):
    """Schema for candidate data as stored in database."""

    @classmethod
    def from_model(cls, candidate: "Candidate") -> "CandidateInDB":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(candidate)
