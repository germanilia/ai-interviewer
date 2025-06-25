"""
CRUD operations for interview sessions.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
from app.models.interview_session import InterviewSession, InterviewSessionStatus

from app.schemas.interview_session import (
    InterviewSessionCreate,
    InterviewSessionUpdate,
    InterviewSessionResponse,
    ChatMessage
)
from app.crud.base import BaseDAO


class InterviewSessionDAO(BaseDAO[InterviewSession, InterviewSessionResponse, InterviewSessionCreate, InterviewSessionUpdate]):
    """Data access object for interview sessions"""

    def __init__(self):
        super().__init__(InterviewSession, InterviewSessionResponse)

    def get(self, db: Session, id: int) -> Optional[InterviewSessionResponse]:
        """Get interview session by ID"""
        session = db.query(self.model).filter(self.model.id == id).first()
        return InterviewSessionResponse.from_model(session) if session else None

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[InterviewSessionResponse]:
        """Get multiple interview sessions with pagination"""
        sessions = (
            db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )
        results = []
        for session in sessions:
            if session:
                result = InterviewSessionResponse.from_model(session)
                if result:
                    results.append(result)
        return results

    def create(self, db: Session, *, obj_in: InterviewSessionCreate, created_by_user_id: int | None = None) -> InterviewSessionResponse:
        """Create a new interview session"""
        db_obj = InterviewSession(
            candidate_id=obj_in.candidate_id,
            interview_id=obj_in.interview_id,
            status=obj_in.status,
            conversation_history=[],
            total_messages=0,
            questions_asked=0
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        result = InterviewSessionResponse.from_model(db_obj)
        if not result:
            raise ValueError("Failed to create interview session")
        return result

    def update(self, db: Session, *, db_obj: InterviewSession, obj_in: InterviewSessionUpdate) -> InterviewSessionResponse:
        """Update an existing interview session"""
        # Get the actual database object if we received a response object
        if isinstance(db_obj, InterviewSessionResponse):
            actual_db_obj = db.query(self.model).filter(self.model.id == db_obj.id).first()
            if not actual_db_obj:
                raise ValueError(f"Session {db_obj.id} not found")
            db_obj = actual_db_obj

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        result = InterviewSessionResponse.from_model(db_obj)
        if not result:
            raise ValueError("Failed to update interview session")
        return result

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete an interview session"""
        session = db.query(self.model).filter(self.model.id == id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False

    def get_by_candidate_and_interview(
        self, 
        db: Session, 
        candidate_id: int, 
        interview_id: int
    ) -> Optional[InterviewSession]:
        """Get interview session by candidate and interview IDs"""
        return db.query(self.model).filter(
            and_(
                self.model.candidate_id == candidate_id,
                self.model.interview_id == interview_id
            )
        ).first()

    def get_active_session(
        self,
        db: Session,
        candidate_id: int,
        interview_id: int
    ) -> Optional[InterviewSessionResponse]:
        """Get active interview session for candidate and interview"""
        session = db.query(self.model).filter(
            and_(
                self.model.candidate_id == candidate_id,
                self.model.interview_id == interview_id,
                self.model.status == InterviewSessionStatus.ACTIVE
            )
        ).first()
        return InterviewSessionResponse.from_model(session) if session else None

    def create_session(
        self,
        db: Session,
        candidate_id: int,
        interview_id: int
    ) -> InterviewSessionResponse:
        """Create a new interview session"""
        session_data = InterviewSessionCreate(
            candidate_id=candidate_id,
            interview_id=interview_id
        )
        return self.create(db=db, obj_in=session_data)

    def add_message_to_conversation(
        self,
        db: Session,
        session_id: int,
        role: str,
        content: str,
        question_id: Optional[int] = None
    ) -> InterviewSessionResponse:
        """Add a message to the conversation history"""
        # Get the actual database object
        db_session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not db_session:
            raise ValueError(f"Session {session_id} not found")

        # Create new message as dict
        new_message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question_id": question_id
        }

        # Update conversation history
        conversation = db_session.conversation_history.copy() if db_session.conversation_history is not None else []
        conversation.append(new_message)

        # Update session directly
        setattr(db_session, 'conversation_history', conversation)
        setattr(db_session, 'total_messages', db_session.total_messages + 1)
        if role == "assistant" and question_id:
            setattr(db_session, 'questions_asked', db_session.questions_asked + 1)

        db.commit()
        db.refresh(db_session)

        result = InterviewSessionResponse.from_model(db_session)
        if not result:
            raise ValueError("Failed to update interview session")
        return result

    def complete_session(self, db: Session, session_id: int) -> InterviewSessionResponse:
        """Mark session as completed and calculate duration"""
        # Get the actual database object
        db_session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not db_session:
            raise ValueError(f"Session {session_id} not found")

        # Calculate session duration
        now = datetime.now(timezone.utc)
        duration_minutes = int((now - db_session.started_at).total_seconds() / 60)

        update_data = InterviewSessionUpdate(
            status=InterviewSessionStatus.COMPLETED,
            completed_at=now,
            session_duration_minutes=duration_minutes
        )

        return self.update(db=db, db_obj=db_session, obj_in=update_data)

    def get_sessions_by_interview(self, db: Session, interview_id: int) -> list[InterviewSession]:
        """Get all sessions for a specific interview"""
        return db.query(self.model).filter(
            self.model.interview_id == interview_id
        ).all()

    def get_sessions_by_candidate(self, db: Session, candidate_id: int) -> list[InterviewSession]:
        """Get all sessions for a specific candidate"""
        return db.query(self.model).filter(
            self.model.candidate_id == candidate_id
        ).all()


# Create instance for dependency injection
interview_session_dao = InterviewSessionDAO()
