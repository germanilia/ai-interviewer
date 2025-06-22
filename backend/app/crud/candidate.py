"""
Candidate DAO for database operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.crud.base import BaseDAO
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateResponse, CandidateCreate, CandidateUpdate, CandidateWithInterviews


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
        candidates = db.query(self.model).offset(skip).limit(limit).all()
        return [CandidateResponse.from_model(candidate) for candidate in candidates]

    def create(self, db: Session, *, obj_in: CandidateCreate) -> CandidateResponse:
        """Create a new candidate."""
        candidate = obj_in.to_model()
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

    def get_with_interviews(self, db: Session, id: int) -> Optional[CandidateWithInterviews]:
        """Get a candidate with their interviews."""
        candidate = db.query(self.model).options(
            joinedload(self.model.interviews)
        ).filter(self.model.id == id).first()

        if candidate:
            return CandidateWithInterviews.from_model(candidate)
        return None

    def search_by_name(self, db: Session, name: str, *, skip: int = 0, limit: int = 100) -> List[CandidateResponse]:
        """Search candidates by name (first or last name)."""
        candidates = db.query(self.model).filter(
            (self.model.first_name.ilike(f"%{name}%")) |
            (self.model.last_name.ilike(f"%{name}%"))
        ).offset(skip).limit(limit).all()
        return [CandidateResponse.from_model(candidate) for candidate in candidates]
