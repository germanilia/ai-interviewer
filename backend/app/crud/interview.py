"""
Interview DAO for database operations.
"""
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app.crud.base import BaseDAO
from app.models.interview import Interview, InterviewStatus
from app.schemas.interview import InterviewResponse, InterviewCreate, InterviewUpdate, InterviewReport


class InterviewDAO(BaseDAO[Interview, InterviewResponse, InterviewCreate, InterviewUpdate]):
    """Data Access Object for Interview operations."""

    def __init__(self):
        super().__init__(Interview, InterviewResponse)

    def get(self, db: Session, id: int) -> Optional[InterviewResponse]:
        """Get an interview by ID."""
        interview = db.query(self.model).filter(self.model.id == id).first()
        return InterviewResponse.from_model(interview) if interview else None

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[InterviewResponse]:
        """Get multiple interviews with pagination."""
        interviews = db.query(self.model).offset(skip).limit(limit).all()
        return [InterviewResponse.from_model(interview) for interview in interviews]

    def create(self, db: Session, *, obj_in: InterviewCreate) -> InterviewResponse:
        """Create a new interview."""
        interview = obj_in.to_model()
        db.add(interview)
        db.commit()
        db.refresh(interview)
        return InterviewResponse.from_model(interview)

    def update(self, db: Session, *, db_obj: Interview, obj_in: InterviewUpdate) -> InterviewResponse:
        """Update an existing interview."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return InterviewResponse.from_model(db_obj)

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete an interview by ID."""
        interview = db.query(self.model).filter(self.model.id == id).first()
        if interview:
            db.delete(interview)
            db.commit()
            return True
        return False



    def get_by_candidate(self, db: Session, candidate_id: int, *, skip: int = 0, limit: int = 100) -> List[InterviewResponse]:
        """Get all interviews for a specific candidate."""
        interviews = db.query(self.model).filter(
            self.model.candidate_id == candidate_id
        ).offset(skip).limit(limit).all()
        return [InterviewResponse.from_model(interview) for interview in interviews]

    def get_by_status(self, db: Session, status: InterviewStatus, *, skip: int = 0, limit: int = 100) -> List[InterviewResponse]:
        """Get interviews by status."""
        interviews = db.query(self.model).filter(
            self.model.status == status
        ).offset(skip).limit(limit).all()
        return [InterviewResponse.from_model(interview) for interview in interviews]

    def complete_interview(self, db: Session, id: int, *, obj_in: InterviewUpdate) -> Optional[InterviewResponse]:
        """Complete an interview with results."""
        interview = db.query(self.model).filter(self.model.id == id).first()
        if not interview:
            return None

        # Update interview with completion data
        update_data = obj_in.model_dump(exclude_unset=True)
        update_data["status"] = InterviewStatus.COMPLETED
        update_data["completed_at"] = datetime.now(timezone.utc)

        for field, value in update_data.items():
            setattr(interview, field, value)

        db.commit()
        db.refresh(interview)
        return InterviewResponse.from_model(interview)

    def get_report(self, db: Session, id: int) -> Optional[InterviewReport]:
        """Get interview report with candidate and job details."""
        interview = db.query(self.model).options(
            joinedload(self.model.candidate),
            joinedload(self.model.job)
        ).filter(self.model.id == id).first()

        if interview and interview.candidate and interview.job:
            # Create a dict with the report data
            report_data = {
                "interview_id": interview.id,
                "candidate_name": f"{interview.candidate.first_name} {interview.candidate.last_name}",
                "candidate_email": interview.candidate.email,
                "job_title": interview.job.title,
                "job_department": interview.job.department,
                "interview_date": interview.interview_date,
                "status": interview.status,
                "score": interview.score,
                "integrity_score": interview.integrity_score,
                "risk_level": interview.risk_level,
                "report_summary": interview.report_summary,
                "risk_indicators": interview.risk_indicators,
                "key_concerns": interview.key_concerns,
                "analysis_notes": interview.analysis_notes,
                "completed_at": interview.completed_at
            }
            return InterviewReport(**report_data)
        return None
