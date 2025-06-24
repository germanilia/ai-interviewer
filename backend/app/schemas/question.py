from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from app.models.interview import QuestionImportance, QuestionCategory

if TYPE_CHECKING:
    from app.models.interview import Question


class QuestionBase(BaseModel):
    """Base question schema with common fields."""
    title: str = Field(..., min_length=1, max_length=500, description="Question title")
    question_text: str = Field(..., min_length=20, max_length=2000, description="Question text content")
    instructions: Optional[str] = Field(None, max_length=1000, description="Instructions for the question")
    importance: QuestionImportance = Field(..., description="Question importance level")
    category: QuestionCategory = Field(..., description="Question category")

    @field_validator("question_text")
    @classmethod
    def validate_question_text_length(cls, v):
        """Validate question text has minimum length."""
        if len(v.strip()) < 20:
            raise ValueError("Question text must be at least 20 characters long")
        return v.strip()

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty."""
        if not v.strip():
            raise ValueError("Title is required")
        return v.strip()


class QuestionCreate(QuestionBase):
    """Schema for creating a new question."""
    created_by_user_id: int

    def to_model(self) -> "Question":
        """Convert Pydantic schema to SQLAlchemy model."""
        from app.models.interview import Question
        return Question(
            title=self.title,
            question_text=self.question_text,
            instructions=self.instructions,
            importance=self.importance,
            category=self.category,
            created_by_user_id=self.created_by_user_id
        )


class QuestionUpdate(BaseModel):
    """Schema for updating a question."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    question_text: Optional[str] = Field(None, min_length=20, max_length=2000)
    instructions: Optional[str] = Field(None, max_length=1000)
    importance: Optional[QuestionImportance] = None
    category: Optional[QuestionCategory] = None

    @field_validator("question_text")
    @classmethod
    def validate_question_text_length(cls, v):
        """Validate question text has minimum length."""
        if v is not None and len(v.strip()) < 20:
            raise ValueError("Question text must be at least 20 characters long")
        return v.strip() if v else v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """Validate title is not empty."""
        if v is not None and not v.strip():
            raise ValueError("Title is required")
        return v.strip() if v else v


class QuestionResponse(QuestionBase):
    """Schema for question responses."""
    id: int
    created_by_user_id: int
    created_by_name: Optional[str] = None  # Will be populated by service layer
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, question: "Question") -> "QuestionResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(question)


class QuestionInDB(QuestionResponse):
    """Schema for question data as stored in database."""

    @classmethod
    def from_model(cls, question: "Question") -> "QuestionInDB":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(question)


class QuestionListResponse(BaseModel):
    """Schema for paginated question list responses."""
    questions: List[QuestionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class QuestionFilter(BaseModel):
    """Schema for question filtering parameters."""
    category: Optional[QuestionCategory] = None
    importance: Optional[QuestionImportance] = None
    search: Optional[str] = Field(None, max_length=100, description="Search term for title or question text")
    created_by_user_id: Optional[int] = None


class BulkQuestionOperation(BaseModel):
    """Schema for bulk operations on questions."""
    question_ids: List[int] = Field(..., description="List of question IDs to operate on")

    @field_validator("question_ids")
    @classmethod
    def validate_question_ids_not_empty(cls, v):
        """Validate that question IDs list is not empty."""
        if not v:
            raise ValueError("At least one question ID is required")
        return v


class BulkQuestionDelete(BulkQuestionOperation):
    """Schema for bulk delete operations."""
    pass


class BulkQuestionCategoryUpdate(BulkQuestionOperation):
    """Schema for bulk category update operations."""
    new_category: QuestionCategory = Field(..., description="New category to assign to selected questions")


class JobQuestionAssignment(BaseModel):
    """Schema for assigning questions to jobs."""
    question_id: int
    job_id: int
    order_index: Optional[int] = Field(None, description="Order of question in job template")


class QuestionImportData(BaseModel):
    """Schema for importing questions from file."""
    questions: List[QuestionCreate]

    @field_validator("questions")
    @classmethod
    def validate_questions_not_empty(cls, v):
        """Validate that questions list is not empty."""
        if not v:
            raise ValueError("At least one question is required for import")
        return v


class QuestionExportFormat(BaseModel):
    """Schema for question export format options."""
    format: str = Field("json", description="Export format")
    include_metadata: bool = Field(True, description="Include creation metadata in export")
    question_ids: Optional[List[int]] = Field(None, description="Specific question IDs to export, if None exports all")

    @field_validator("format")
    @classmethod
    def validate_format(cls, v):
        """Validate export format."""
        allowed_formats = ["json", "csv", "xlsx"]
        if v not in allowed_formats:
            raise ValueError(f"Format must be one of: {', '.join(allowed_formats)}")
        return v
