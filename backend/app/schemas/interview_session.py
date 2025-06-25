"""
Interview session schemas for API requests and responses.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.interview_session import InterviewSessionStatus


class ChatMessage(BaseModel):
    """Individual chat message schema"""
    role: str  # "assistant" or "user"
    content: str
    timestamp: datetime
    question_id: Optional[int] = None


class InterviewSessionBase(BaseModel):
    """Base interview session schema"""
    candidate_id: int
    interview_id: int
    status: InterviewSessionStatus = InterviewSessionStatus.ACTIVE


class InterviewSessionCreate(InterviewSessionBase):
    """Schema for creating a new interview session"""
    pass


class InterviewSessionUpdate(BaseModel):
    """Schema for updating an interview session"""
    status: Optional[InterviewSessionStatus] = None
    conversation_history: Optional[list[dict]] = None  # Store as dict for JSON compatibility
    completed_at: Optional[datetime] = None
    total_messages: Optional[int] = None
    questions_asked: Optional[int] = None
    session_duration_minutes: Optional[int] = None


class InterviewSessionResponse(InterviewSessionBase):
    """Complete interview session response schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_history: list[ChatMessage]
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_activity_at: datetime
    total_messages: int
    questions_asked: int
    session_duration_minutes: Optional[int] = None

    @classmethod
    def from_model(cls, session) -> Optional["InterviewSessionResponse"]:
        """Convert from SQLAlchemy model to Pydantic schema"""
        if not session:
            return None

        # Convert conversation history from dict to ChatMessage objects
        conversation_history = []
        if session.conversation_history:
            for msg in session.conversation_history:
                conversation_history.append(ChatMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp"),
                    question_id=msg.get("question_id")
                ))

        return cls(
            id=session.id,
            candidate_id=session.candidate_id,
            interview_id=session.interview_id,
            status=session.status,
            conversation_history=conversation_history,
            started_at=session.started_at,
            completed_at=session.completed_at,
            last_activity_at=session.last_activity_at,
            total_messages=session.total_messages,
            questions_asked=session.questions_asked,
            session_duration_minutes=session.session_duration_minutes
        )


# Keep the old name for backward compatibility
InterviewSession = InterviewSessionResponse


class CandidateLoginRequest(BaseModel):
    """Request schema for candidate login using pass key"""
    pass_key: str


class CandidateLoginResponse(BaseModel):
    """Response schema for candidate login"""
    candidate_id: int
    candidate_name: str
    interview_id: int
    interview_title: str
    session_id: Optional[int] = None  # Existing session if any
    message: str


class ChatRequest(BaseModel):
    """Request schema for chat messages"""
    session_id: int
    message: str
    language: Optional[str] = "en"  # Language preference: 'en', 'he', 'ar', 'other'


class ChatResponse(BaseModel):
    """Response schema for chat messages"""
    session_id: int
    assistant_message: str
    session_status: InterviewSessionStatus
    is_interview_complete: bool = False


class InterviewContext(BaseModel):
    """Interview context for LLM processing"""
    candidate_name: str
    interview_title: str
    job_description: Optional[str] = None
    questions: list[str]
    conversation_history: list[ChatMessage]
