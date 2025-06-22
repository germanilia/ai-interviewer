from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.interview import QuestionImportance, QuestionCategory

if TYPE_CHECKING:
    from app.models.interview import Question


class QuestionBase(BaseModel):
    """Base question schema with common fields."""
    title: str
    question_text: str
    instructions: Optional[str] = None
    importance: QuestionImportance
    category: QuestionCategory


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
    title: Optional[str] = None
    question_text: Optional[str] = None
    instructions: Optional[str] = None
    importance: Optional[QuestionImportance] = None
    category: Optional[QuestionCategory] = None


class QuestionResponse(QuestionBase):
    """Schema for question responses."""
    id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, question: "Question") -> "QuestionResponse":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(question)


class QuestionWithCreator(QuestionResponse):
    """Schema for question with creator details included."""
    from app.schemas.user import UserResponse
    created_by: UserResponse

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, question: "Question") -> "QuestionWithCreator":
        """Convert SQLAlchemy model to Pydantic schema with creator."""
        return cls.model_validate(question)


class QuestionInDB(QuestionResponse):
    """Schema for question data as stored in database."""
    
    @classmethod
    def from_model(cls, question: "Question") -> "QuestionInDB":
        """Convert SQLAlchemy model to Pydantic schema."""
        return cls.model_validate(question)
