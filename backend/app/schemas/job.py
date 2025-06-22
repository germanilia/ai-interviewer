from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.interview import Job
    from app.schemas.job_question import JobQuestionResponse


class JobBase(BaseModel):
    """Base job schema with common fields."""
    title: str
    description: Optional[str] = None
    department: Optional[str] = None


class JobCreate(JobBase):
    """Schema for creating a new job."""
    created_by_user_id: int
    
    def to_model(self) -> "Job":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.interview import Job
        return Job(
            title=self.title,
            description=self.description,
            department=self.department,
            created_by_user_id=self.created_by_user_id
        )


class JobUpdate(BaseModel):
    """Schema for updating a job."""
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None


class JobResponse(JobBase):
    """Schema for job responses."""
    id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, job: "Job") -> "JobResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(job)


class JobWithQuestions(JobResponse):
    """Schema for job with questions template included."""
    job_questions: list["JobQuestionResponse"] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, job: "Job") -> "JobWithQuestions":
        """Convert SQLAlchemy model to Pydantic schema with questions."""
        return cls.model_validate(job)


class JobInDB(JobResponse):
    """Schema for job data as stored in database."""

    @classmethod
    def from_model(cls, job: "Job") -> "JobInDB":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(job)
