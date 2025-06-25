"""
Interview DAO for database operations.
"""
from typing import Optional, List, Dict
from datetime import datetime, timezone
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from app.crud.base import BaseDAO
from app.models.interview import Interview, InterviewStatus
from app.models.candidate import Candidate
from app.schemas.interview import InterviewResponse, InterviewCreate, InterviewUpdate, InterviewReport


class InterviewDAO(BaseDAO[Interview, InterviewResponse, InterviewCreate, InterviewUpdate]):
    """Data Access Object for Interview operations."""

    def __init__(self):
        super().__init__(Interview, InterviewResponse)

    def get(self, db: Session, id: int) -> Optional[InterviewResponse]:
        """Get an interview by ID."""
        interview = db.query(self.model).filter(self.model.id == id).first()
        return InterviewResponse.from_model(interview) if interview else None

    def get_model(self, db: Session, id: int) -> Optional[Interview]:
        """Get an interview model by ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[InterviewResponse]:
        """Get multiple interviews with pagination."""
        interviews = db.query(self.model).offset(skip).limit(limit).all()
        return [InterviewResponse.from_model(interview) for interview in interviews]

    def create(self, db: Session, *, obj_in: InterviewCreate, created_by_user_id: int | None = None) -> InterviewResponse:
        """Create a new interview."""
        if created_by_user_id is None:
            raise ValueError("created_by_user_id is required")
        interview = obj_in.to_model(created_by_user_id=created_by_user_id)
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

    def get_by_candidate(self, db: Session, candidate_id: int) -> List[InterviewResponse]:
        """Get interview for a specific candidate (candidates are now assigned to one interview)."""
        # Get the candidate first to find their assigned interview
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate or candidate.interview_id is None:
            return []

        interview = db.query(self.model).filter(self.model.id == candidate.interview_id).first()
        return [InterviewResponse.from_model(interview)] if interview else []

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
        """Get interview report with assigned candidates details."""
        interview = db.query(self.model).filter(self.model.id == id).first()

        if interview and interview.candidate:
            # Create a dict with the report data
            report_data = {
                "interview_id": interview.id,
                "candidate_name": f"{interview.candidate.first_name} {interview.candidate.last_name}",
                "candidate_email": interview.candidate.email,
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

    def get_interviews_paginated(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        candidate_id: Optional[int] = None,
    ) -> tuple[List[Interview], int]:
        """
        Get interviews with pagination, search, and filtering.
        Returns a tuple of (interviews, total_count).
        """
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        skip = (page - 1) * page_size

        # Base query for interviews
        query = db.query(self.model)

        filters = []

        # Note: Interviews don't have status in the new model - they contain job info
        # Status is now on candidates who are assigned to interviews

        if candidate_id:
            # Filter interviews that have this candidate assigned
            filters.append(
                db.query(Candidate).filter(
                    Candidate.interview_id == self.model.id,
                    Candidate.id == candidate_id
                ).exists()
            )

        if search:
            # Search in job title, description, or department
            search_filter = or_(
                func.lower(self.model.job_title).contains(search.lower()),
                func.lower(self.model.job_description).contains(search.lower()),
                func.lower(self.model.job_department).contains(search.lower()),
            )
            filters.append(search_filter)

        if filters:
            query = query.filter(and_(*filters))

        total = query.count()
        interviews = (
            query.order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(page_size)
            .all()
        )
        return interviews, total

    def get_status_counts(
        self,
        db: Session,
        candidate_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, int]:
        """Get count of interviews by completion status."""
        base_query = db.query(self.model)

        filters = []
        if candidate_id:
            # Filter interviews that have this candidate assigned
            filters.append(
                db.query(Candidate).filter(
                    Candidate.interview_id == self.model.id,
                    Candidate.id == candidate_id
                ).exists()
            )

        if search:
            # Search in job title, description, or department
            search_filter = or_(
                func.lower(self.model.job_title).contains(search.lower()),
                func.lower(self.model.job_description).contains(search.lower()),
                func.lower(self.model.job_department).contains(search.lower()),
            )
            filters.append(search_filter)

        if filters:
            base_query = base_query.filter(and_(*filters))

        # Since interviews don't have status anymore, we'll categorize by completion
        total_count = base_query.count()
        completed_count = base_query.filter(self.model.completed_candidates == self.model.total_candidates).count()
        in_progress_count = base_query.filter(
            and_(
                self.model.completed_candidates > 0,
                self.model.completed_candidates < self.model.total_candidates
            )
        ).count()
        pending_count = base_query.filter(self.model.completed_candidates == 0).count()

        return {
            "all": total_count,
            "completed": completed_count,
            "in_progress": in_progress_count,
            "pending": pending_count,
        }
