from pydantic import BaseModel, ConfigDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.interview import JobQuestion


class JobQuestionBase(BaseModel):
    """Base job question schema with common fields."""
    job_id: int
    question_id: int
    order_index: int


class JobQuestionCreate(JobQuestionBase):
    """Schema for creating a new job question."""
    
    def to_model(self) -> "JobQuestion":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.interview import JobQuestion
        return JobQuestion(
            job_id=self.job_id,
            question_id=self.question_id,
            order_index=self.order_index
        )


class JobQuestionUpdate(BaseModel):
    """Schema for updating a job question."""
    order_index: int


class JobQuestionResponse(JobQuestionBase):
    """Schema for job question responses."""
    id: int

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, job_question: "JobQuestion") -> "JobQuestionResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(job_question)


class JobQuestionInDB(JobQuestionResponse):
    """Schema for job question data as stored in database."""

    @classmethod
    def from_model(cls, job_question: "JobQuestion") -> "JobQuestionInDB":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(job_question)
