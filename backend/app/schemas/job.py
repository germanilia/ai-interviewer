from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime

if TYPE_CHECKING:
    from app.models.interview import Job
    from app.schemas.job_question import JobQuestionResponse


class JobBase(BaseModel):
    """Base job schema with common fields."""
    title: str
    description: Optional[str] = None
    department: Optional[str] = None


class JobCreateRequest(JobBase):
    """Schema for job creation request (without user ID)."""
    pass


class JobCreate(JobBase):
    """Schema for creating a new job (internal use with user ID)."""
    created_by_user_id: Optional[int] = None

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


class JobListResponse(BaseModel):
    """Schema for paginated job list response."""
    jobs: list[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class JobFilter(BaseModel):
    """Schema for job filtering parameters."""
    search: Optional[str] = None
    department: Optional[str] = None
    created_by_user_id: Optional[int] = None


class JobStatistics(BaseModel):
    """Schema for job statistics."""
    total_interviews: int
    avg_score: Optional[float] = None
    completion_rate: float
    avg_completion_time: Optional[float] = None  # in minutes
    questions_count: int


class JobCloneRequest(BaseModel):
    """Schema for cloning job template."""
    source_job_id: int
    target_job_id: int
    clone_questions: bool = True
