from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Any, TYPE_CHECKING, List
from datetime import datetime
import secrets
import string
from app.models.interview import InterviewStatus, IntegrityScore, RiskLevel, InterviewLanguage

if TYPE_CHECKING:
    from app.models.interview import Interview


def generate_pass_key() -> str:
    """Generate a unique 8-character alphanumeric pass key."""
    characters = string.ascii_uppercase + string.digits
    # Exclude confusing characters like 0, O, I, 1
    characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(characters) for _ in range(8))


class InterviewBase(BaseModel):
    """Base interview schema with common fields including job information."""
    # Job information (merged from Job model)
    job_title: str
    job_description: Optional[str] = None
    job_department: Optional[str] = None

    # Interview language
    language: InterviewLanguage = InterviewLanguage.HEBREW

    # General interview instructions
    instructions: Optional[str] = None


class InterviewCreate(InterviewBase):
    """Schema for creating a new interview."""
    question_ids: list[int] = Field(..., min_length=1, description="List of question IDs to include in the interview")

    @field_validator("question_ids")
    @classmethod
    def validate_question_ids(cls, v):
        """Validate that question_ids is not empty and contains valid IDs."""
        if not v:
            raise ValueError("At least one question is required for an interview")
        if len(v) == 0:
            raise ValueError("At least one question is required for an interview")
        # Check for duplicate question IDs
        if len(v) != len(set(v)):
            raise ValueError("Duplicate question IDs are not allowed")
        # Check for invalid question IDs (negative or zero)
        if any(qid <= 0 for qid in v):
            raise ValueError("Question IDs must be positive integers")
        return v

    def to_model(self, created_by_user_id: int) -> "Interview":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.interview import Interview
        return Interview(
            job_title=self.job_title,
            job_description=self.job_description,
            job_department=self.job_department,
            language=self.language,
            instructions=self.instructions,
            created_by_user_id=created_by_user_id
        )


class InterviewUpdate(BaseModel):
    """Schema for updating an interview."""
    # Job fields
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    job_department: Optional[str] = None

    # Interview language
    language: Optional[InterviewLanguage] = None

    # General interview fields
    instructions: Optional[str] = None
    avg_score: Optional[int] = None
    total_candidates: Optional[int] = None
    completed_candidates: Optional[int] = None


class InterviewResponse(InterviewBase):
    """Schema for interview responses."""
    id: int
    avg_score: Optional[int] = None
    total_candidates: int = 0
    completed_candidates: int = 0
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
    interview_date: Optional[datetime]
    status: InterviewStatus
    score: Optional[float]
    integrity_score: Optional[IntegrityScore]
    risk_level: Optional[RiskLevel]
    report_summary: Optional[str]
    risk_indicators: Optional[list[dict[str, Any]]]
    key_concerns: Optional[list[dict[str, Any]]]
    analysis_notes: Optional[str]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class InterviewWithDetails(InterviewResponse):
    """Enhanced interview response with assigned candidates and questions."""
    assigned_candidates: Optional[list[dict[str, Any]]] = None
    candidates_count: int = 0
    questions: Optional[list[dict[str, Any]]] = None
    questions_count: int = 0

    @classmethod
    def from_model_with_details(cls, interview: "Interview", candidates: Optional[list] = None, questions: Optional[list] = None) -> "InterviewWithDetails":
        """Convert SQLAlchemy model to Pydantic schema with assigned candidates and questions."""
        instance = cls.model_validate(interview)

        # Populate assigned candidates
        if candidates:
            instance.assigned_candidates = [
                {
                    "id": candidate.id,
                    "name": f"{candidate.first_name} {candidate.last_name}",
                    "email": candidate.email,
                    "status": candidate.interview_status,
                    "pass_key": candidate.pass_key,
                    "score": candidate.score,
                }
                for candidate in candidates
            ]
            instance.candidates_count = len(candidates)
        else:
            instance.assigned_candidates = []
            instance.candidates_count = getattr(interview, 'total_candidates', 0) or 0

        # Populate questions
        if questions:
            instance.questions = [
                {
                    "id": question.id,
                    "title": question.title,
                    "question_text": question.question_text,
                    "importance": question.importance,
                    "category": question.category,
                    "order_index": getattr(question, 'order_index', 0),
                }
                for question in questions
            ]
            instance.questions_count = len(questions)
        else:
            instance.questions = []
            instance.questions_count = 0

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
