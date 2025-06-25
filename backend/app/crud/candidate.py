"""
Candidate DAO for database operations.
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.crud.base import BaseDAO
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateResponse, CandidateCreate, CandidateUpdate


class CandidateDAO(BaseDAO[Candidate, CandidateResponse, CandidateCreate, CandidateUpdate]):
    """Data Access Object for Candidate operations."""

    def __init__(self):
        super().__init__(Candidate, CandidateResponse)

    def get(self, db: Session, id: int) -> Optional[CandidateResponse]:
        """Get a candidate by ID."""
        candidate = db.query(self.model).filter(self.model.id == id).first()
        return CandidateResponse.from_model(candidate) if candidate else None

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[CandidateResponse]:
        """Get multiple candidates with pagination."""
        candidates = (
            db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [CandidateResponse.from_model(candidate) for candidate in candidates]

    def get_multi_with_search(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[CandidateResponse], int]:
        """Get candidates with search, filtering, and pagination."""
        query = db.query(self.model)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.first_name.ilike(search_term),
                    self.model.last_name.ilike(search_term),
                    self.model.email.ilike(search_term),
                    func.concat(self.model.first_name, ' ', self.model.last_name).ilike(search_term)
                )
            )

        # Apply status filter (this would need to be implemented based on interview status)
        if status and status != 'all':
            # This is a simplified implementation - in reality, you'd join with interviews
            # and filter based on the most recent interview status
            pass

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        candidates = query.offset(skip).limit(limit).all()

        return [CandidateResponse.from_model(candidate) for candidate in candidates], total

    def create(self, db: Session, *, obj_in: CandidateCreate, created_by_user_id: int | None = None) -> CandidateResponse:
        """Create a new candidate."""
        if created_by_user_id is None:
            raise ValueError("created_by_user_id is required")
        candidate = obj_in.to_model(created_by_user_id=created_by_user_id)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return CandidateResponse.from_model(candidate)

    def update(self, db: Session, *, db_obj: Candidate, obj_in: CandidateUpdate) -> CandidateResponse:
        """Update an existing candidate."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return CandidateResponse.from_model(db_obj)

    def update_by_id(self, db: Session, id: int, obj_in: CandidateUpdate) -> Optional[CandidateResponse]:
        """Update a candidate by ID."""
        candidate = db.query(self.model).filter(self.model.id == id).first()
        if candidate:
            return self.update(db, db_obj=candidate, obj_in=obj_in)
        return None

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete a candidate by ID."""
        candidate = db.query(self.model).filter(self.model.id == id).first()
        if candidate:
            db.delete(candidate)
            db.commit()
            return True
        return False

    def get_by_email(self, db: Session, email: str) -> Optional[CandidateResponse]:
        """Get a candidate by email."""
        candidate = db.query(self.model).filter(self.model.email == email).first()
        return CandidateResponse.from_model(candidate) if candidate else None

    def get_by_pass_key(self, db: Session, pass_key: str) -> Optional[CandidateResponse]:
        """Get a candidate by pass key."""
        candidate = db.query(self.model).filter(self.model.pass_key == pass_key).first()
        return CandidateResponse.from_model(candidate) if candidate else None

    def get_interview_history(self, db: Session, candidate_id: int) -> List:
        """Get interview assignment for a candidate."""
        from app.models.interview import Interview

        candidate = db.query(self.model).filter(self.model.id == candidate_id).first()
        if not candidate or candidate.interview_id is None:
            return []

        # Get the assigned interview
        interview = db.query(Interview).filter(Interview.id == candidate.interview_id).first()
        if interview:
            return [
                {
                    "id": interview.id,
                    "job_title": interview.job_title,
                    "job_department": interview.job_department,
                    "created_at": interview.created_at,
                    "interview_status": candidate.interview_status,
                    "interview_date": candidate.interview_date,
                    "score": candidate.score,
                }
            ]
        return []



    def search_by_name(self, db: Session, name: str, *, skip: int = 0, limit: int = 100) -> List[CandidateResponse]:
        """Search candidates by name (first or last name)."""
        candidates = db.query(self.model).filter(
            (self.model.first_name.ilike(f"%{name}%")) |
            (self.model.last_name.ilike(f"%{name}%"))
        ).offset(skip).limit(limit).all()
        return [CandidateResponse.from_model(candidate) for candidate in candidates]
