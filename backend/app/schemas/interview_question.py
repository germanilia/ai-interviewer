from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, TYPE_CHECKING
from datetime import datetime
from app.models.interview import InterviewQuestionStatus

if TYPE_CHECKING:
    from app.models.interview import InterviewQuestion


class InterviewQuestionBase(BaseModel):
    """Base interview question schema with common fields."""
    interview_id: int
    question_id: int
    status: InterviewQuestionStatus = InterviewQuestionStatus.PENDING
    order_index: int
    question_text_snapshot: str


class InterviewQuestionCreate(InterviewQuestionBase):
    """Schema for creating a new interview question."""
    
    def to_model(self) -> "InterviewQuestion":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.interview import InterviewQuestion
        return InterviewQuestion(
            interview_id=self.interview_id,
            question_id=self.question_id,
            status=self.status,
            order_index=self.order_index,
            question_text_snapshot=self.question_text_snapshot
        )


class InterviewQuestionUpdate(BaseModel):
    """Schema for updating an interview question."""
    status: Optional[InterviewQuestionStatus] = None
    candidate_answer: Optional[str] = None
    ai_analysis: Optional[dict[str, Any]] = None
    follow_up_questions: Optional[dict[str, Any]] = None
    asked_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None


class InterviewQuestionResponse(InterviewQuestionBase):
    """Schema for interview question responses."""
    id: int
    candidate_answer: Optional[str] = None
    ai_analysis: Optional[dict[str, Any]] = None
    follow_up_questions: Optional[dict[str, Any]] = None
    asked_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, interview_question: "InterviewQuestion") -> "InterviewQuestionResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(interview_question)


class InterviewQuestionInDB(InterviewQuestionResponse):
    """Schema for interview question data as stored in database."""

    @classmethod
    def from_model(cls, interview_question: "InterviewQuestion") -> "InterviewQuestionInDB":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(interview_question)
