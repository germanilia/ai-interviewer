"""
InterviewQuestion DAO for database operations.
"""
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.crud.base import BaseDAO
from app.models.interview import InterviewQuestion, InterviewQuestionStatus
from app.schemas.interview_question import InterviewQuestionResponse, InterviewQuestionCreate, InterviewQuestionUpdate


class InterviewQuestionDAO(BaseDAO[InterviewQuestion, InterviewQuestionResponse, InterviewQuestionCreate, InterviewQuestionUpdate]):
    """Data Access Object for InterviewQuestion operations."""

    def __init__(self):
        super().__init__(InterviewQuestion, InterviewQuestionResponse)

    def get(self, db: Session, id: int) -> Optional[InterviewQuestionResponse]:
        """Get an interview question by ID."""
        interview_question = db.query(self.model).filter(self.model.id == id).first()
        return InterviewQuestionResponse.from_model(interview_question) if interview_question else None

    def get_model(self, db: Session, id: int) -> Optional[InterviewQuestion]:
        """Get an interview question model by ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[InterviewQuestionResponse]:
        """Get multiple interview questions with pagination."""
        interview_questions = db.query(self.model).offset(skip).limit(limit).all()
        return [InterviewQuestionResponse.from_model(iq) for iq in interview_questions]

    def create(self, db: Session, *, obj_in: InterviewQuestionCreate, created_by_user_id: int | None = None) -> InterviewQuestionResponse:
        """Create a new interview question."""
        interview_question = obj_in.to_model()
        db.add(interview_question)
        db.commit()
        db.refresh(interview_question)
        return InterviewQuestionResponse.from_model(interview_question)

    def update(self, db: Session, *, db_obj: InterviewQuestion, obj_in: InterviewQuestionUpdate) -> InterviewQuestionResponse:
        """Update an existing interview question."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return InterviewQuestionResponse.from_model(db_obj)

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete an interview question by ID."""
        interview_question = db.query(self.model).filter(self.model.id == id).first()
        if interview_question:
            db.delete(interview_question)
            db.commit()
            return True
        return False



    def get_by_interview(self, db: Session, interview_id: int, *, skip: int = 0, limit: int = 100) -> List[InterviewQuestionResponse]:
        """Get all questions for a specific interview, ordered by order_index."""
        interview_questions = db.query(self.model).filter(
            self.model.interview_id == interview_id
        ).order_by(self.model.order_index).offset(skip).limit(limit).all()
        return [InterviewQuestionResponse.from_model(iq) for iq in interview_questions]

    def get_by_status(self, db: Session, interview_id: int, status: InterviewQuestionStatus, *, skip: int = 0, limit: int = 100) -> List[InterviewQuestionResponse]:
        """Get interview questions by status."""
        interview_questions = db.query(self.model).filter(
            self.model.interview_id == interview_id,
            self.model.status == status
        ).order_by(self.model.order_index).offset(skip).limit(limit).all()
        return [InterviewQuestionResponse.from_model(iq) for iq in interview_questions]

    def get_next_question(self, db: Session, interview_id: int) -> Optional[InterviewQuestionResponse]:
        """Get the next pending question for an interview."""
        interview_question = db.query(self.model).filter(
            self.model.interview_id == interview_id,
            self.model.status == InterviewQuestionStatus.PENDING
        ).order_by(self.model.order_index).first()
        
        return InterviewQuestionResponse.from_model(interview_question) if interview_question else None

    def mark_as_asked(self, db: Session, id: int) -> Optional[InterviewQuestionResponse]:
        """Mark a question as asked."""
        interview_question = db.query(self.model).filter(self.model.id == id).first()
        if interview_question:
            interview_question.status = InterviewQuestionStatus.ASKED  # type: ignore
            interview_question.asked_at = datetime.now(timezone.utc)  # type: ignore
            db.commit()
            db.refresh(interview_question)
            return InterviewQuestionResponse.from_model(interview_question)
        return None

    def mark_as_answered(self, db: Session, id: int, *, answer: str, ai_analysis: Optional[dict] = None) -> Optional[InterviewQuestionResponse]:
        """Mark a question as answered with the candidate's response."""
        interview_question = db.query(self.model).filter(self.model.id == id).first()
        if interview_question:
            interview_question.status = InterviewQuestionStatus.ANSWERED  # type: ignore
            interview_question.candidate_answer = answer  # type: ignore
            interview_question.answered_at = datetime.now(timezone.utc)  # type: ignore
            if ai_analysis:
                interview_question.ai_analysis = ai_analysis  # type: ignore
            db.commit()
            db.refresh(interview_question)
            return InterviewQuestionResponse.from_model(interview_question)
        return None

    def mark_as_skipped(self, db: Session, id: int) -> Optional[InterviewQuestionResponse]:
        """Mark a question as skipped."""
        interview_question = db.query(self.model).filter(self.model.id == id).first()
        if interview_question:
            interview_question.status = InterviewQuestionStatus.SKIPPED  # type: ignore
            db.commit()
            db.refresh(interview_question)
            return InterviewQuestionResponse.from_model(interview_question)
        return None

    def add_follow_up_questions(self, db: Session, id: int, *, follow_ups: dict) -> Optional[InterviewQuestionResponse]:
        """Add follow-up questions generated by AI."""
        interview_question = db.query(self.model).filter(self.model.id == id).first()
        if interview_question:
            interview_question.follow_up_questions = follow_ups  # type: ignore
            db.commit()
            db.refresh(interview_question)
            return InterviewQuestionResponse.from_model(interview_question)
        return None

    def bulk_create_from_job_template(self, db: Session, interview_id: int, job_questions: List[dict]) -> List[InterviewQuestionResponse]:
        """
        Create interview questions from job template.
        job_questions should be a list of dicts with job question data.
        """
        interview_questions = []
        
        for jq_data in job_questions:
            interview_question = InterviewQuestion(
                interview_id=interview_id,
                question_id=jq_data['question_id'],
                order_index=jq_data['order_index'],
                question_text_snapshot=jq_data['question_text'],  # Snapshot of question text
                status=InterviewQuestionStatus.PENDING
            )
            interview_questions.append(interview_question)
            db.add(interview_question)
        
        db.commit()
        
        # Refresh all created objects
        for iq in interview_questions:
            db.refresh(iq)
            
        return [InterviewQuestionResponse.from_model(iq) for iq in interview_questions]

    def get_interview_progress(self, db: Session, interview_id: int) -> dict:
        """Get interview progress statistics."""
        total = db.query(self.model).filter(self.model.interview_id == interview_id).count()
        answered = db.query(self.model).filter(
            self.model.interview_id == interview_id,
            self.model.status == InterviewQuestionStatus.ANSWERED
        ).count()
        asked = db.query(self.model).filter(
            self.model.interview_id == interview_id,
            self.model.status == InterviewQuestionStatus.ASKED
        ).count()
        skipped = db.query(self.model).filter(
            self.model.interview_id == interview_id,
            self.model.status == InterviewQuestionStatus.SKIPPED
        ).count()
        pending = db.query(self.model).filter(
            self.model.interview_id == interview_id,
            self.model.status == InterviewQuestionStatus.PENDING
        ).count()
        
        return {
            "total": total,
            "answered": answered,
            "asked": asked,
            "skipped": skipped,
            "pending": pending,
            "completion_percentage": (answered / total * 100) if total > 0 else 0
        }
