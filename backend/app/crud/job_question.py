"""
JobQuestion DAO for database operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import BaseDAO
from app.models.interview import JobQuestion
from app.schemas.job_question import JobQuestionResponse, JobQuestionCreate, JobQuestionUpdate


class JobQuestionDAO(BaseDAO[JobQuestion, JobQuestionResponse, JobQuestionCreate, JobQuestionUpdate]):
    """Data Access Object for JobQuestion operations."""

    def __init__(self):
        super().__init__(JobQuestion, JobQuestionResponse)

    def get(self, db: Session, id: int) -> Optional[JobQuestionResponse]:
        """Get a job question by ID."""
        job_question = db.query(self.model).filter(self.model.id == id).first()
        return JobQuestionResponse.from_model(job_question) if job_question else None

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[JobQuestionResponse]:
        """Get multiple job questions with pagination."""
        job_questions = db.query(self.model).offset(skip).limit(limit).all()
        return [JobQuestionResponse.from_model(jq) for jq in job_questions]

    def create(self, db: Session, *, obj_in: JobQuestionCreate) -> JobQuestionResponse:
        """Create a new job question."""
        job_question = obj_in.to_model()
        db.add(job_question)
        db.commit()
        db.refresh(job_question)
        return JobQuestionResponse.from_model(job_question)

    def update(self, db: Session, *, db_obj: JobQuestion, obj_in: JobQuestionUpdate) -> JobQuestionResponse:
        """Update an existing job question."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return JobQuestionResponse.from_model(db_obj)

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete a job question by ID."""
        job_question = db.query(self.model).filter(self.model.id == id).first()
        if job_question:
            db.delete(job_question)
            db.commit()
            return True
        return False



    def get_by_job(self, db: Session, job_id: int, *, skip: int = 0, limit: int = 100) -> List[JobQuestionResponse]:
        """Get all questions for a specific job, ordered by order_index."""
        job_questions = db.query(self.model).filter(
            self.model.job_id == job_id
        ).order_by(self.model.order_index).offset(skip).limit(limit).all()
        return [JobQuestionResponse.from_model(jq) for jq in job_questions]

    def get_by_question(self, db: Session, question_id: int, *, skip: int = 0, limit: int = 100) -> List[JobQuestionResponse]:
        """Get all jobs that use a specific question."""
        job_questions = db.query(self.model).filter(
            self.model.question_id == question_id
        ).offset(skip).limit(limit).all()
        return [JobQuestionResponse.from_model(jq) for jq in job_questions]

    def reorder_questions(self, db: Session, job_id: int, question_orders: List[dict]) -> List[JobQuestionResponse]:
        """
        Reorder questions for a job.
        question_orders should be a list of dicts with 'id' and 'order_index' keys.
        """
        updated_questions = []
        
        for order_data in question_orders:
            job_question = db.query(self.model).filter(
                self.model.id == order_data['id'],
                self.model.job_id == job_id
            ).first()
            
            if job_question:
                job_question.order_index = order_data['order_index']
                updated_questions.append(job_question)
        
        db.commit()
        
        # Refresh all updated objects
        for jq in updated_questions:
            db.refresh(jq)
            
        return [JobQuestionResponse.from_model(jq) for jq in updated_questions]

    def bulk_create_for_job(self, db: Session, job_id: int, question_ids: List[int]) -> List[JobQuestionResponse]:
        """
        Create multiple job questions for a job at once.
        Questions will be ordered by the order they appear in the list.
        """
        job_questions = []
        
        for index, question_id in enumerate(question_ids):
            job_question = JobQuestion(
                job_id=job_id,
                question_id=question_id,
                order_index=index + 1
            )
            job_questions.append(job_question)
            db.add(job_question)
        
        db.commit()
        
        # Refresh all created objects
        for jq in job_questions:
            db.refresh(jq)
            
        return [JobQuestionResponse.from_model(jq) for jq in job_questions]

    def delete_all_for_job(self, db: Session, job_id: int) -> bool:
        """Delete all questions for a specific job."""
        deleted_count = db.query(self.model).filter(self.model.job_id == job_id).delete()
        db.commit()
        return deleted_count > 0
