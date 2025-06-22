"""
Job DAO for database operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.crud.base import BaseDAO
from app.models.interview import Job
from app.schemas.job import JobResponse, JobCreate, JobUpdate, JobWithCreator, JobWithQuestions


class JobDAO(BaseDAO[Job, JobResponse, JobCreate, JobUpdate]):
    """Data Access Object for Job operations."""

    def __init__(self):
        super().__init__(Job, JobResponse)

    def get(self, db: Session, id: int) -> Optional[JobResponse]:
        """Get a job by ID."""
        job = db.query(self.model).filter(self.model.id == id).first()
        return JobResponse.from_model(job) if job else None

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[JobResponse]:
        """Get multiple jobs with pagination."""
        jobs = db.query(self.model).offset(skip).limit(limit).all()
        return [JobResponse.from_model(job) for job in jobs]

    def create(self, db: Session, *, obj_in: JobCreate) -> JobResponse:
        """Create a new job."""
        job = obj_in.to_model()
        db.add(job)
        db.commit()
        db.refresh(job)
        return JobResponse.from_model(job)

    def update(self, db: Session, *, db_obj: Job, obj_in: JobUpdate) -> JobResponse:
        """Update an existing job."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return JobResponse.from_model(db_obj)

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete a job by ID."""
        job = db.query(self.model).filter(self.model.id == id).first()
        if job:
            db.delete(job)
            db.commit()
            return True
        return False

    def get_with_creator(self, db: Session, id: int) -> Optional[JobWithCreator]:
        """Get a job with creator details."""
        job = db.query(self.model).options(
            joinedload(self.model.created_by)
        ).filter(self.model.id == id).first()
        
        if job:
            return JobWithCreator.from_model(job)
        return None

    def get_with_questions(self, db: Session, id: int) -> Optional[JobWithQuestions]:
        """Get a job with its question template."""
        job = db.query(self.model).options(
            joinedload(self.model.job_questions)
        ).filter(self.model.id == id).first()
        
        if job:
            return JobWithQuestions.from_model(job)
        return None

    def get_by_creator(self, db: Session, creator_id: int, *, skip: int = 0, limit: int = 100) -> List[JobResponse]:
        """Get jobs created by a specific user."""
        jobs = db.query(self.model).filter(
            self.model.created_by_user_id == creator_id
        ).offset(skip).limit(limit).all()
        return [JobResponse.from_model(job) for job in jobs]

    def get_by_department(self, db: Session, department: str, *, skip: int = 0, limit: int = 100) -> List[JobResponse]:
        """Get jobs by department."""
        jobs = db.query(self.model).filter(
            self.model.department == department
        ).offset(skip).limit(limit).all()
        return [JobResponse.from_model(job) for job in jobs]

    def search_by_title(self, db: Session, title: str, *, skip: int = 0, limit: int = 100) -> List[JobResponse]:
        """Search jobs by title."""
        jobs = db.query(self.model).filter(
            self.model.title.ilike(f"%{title}%")
        ).offset(skip).limit(limit).all()
        return [JobResponse.from_model(job) for job in jobs]

    def get_by_filters(self, db: Session, *, department: Optional[str] = None, 
                      creator_id: Optional[int] = None,
                      skip: int = 0, limit: int = 100) -> List[JobResponse]:
        """Get jobs with multiple filters."""
        query = db.query(self.model)
        
        if department:
            query = query.filter(self.model.department == department)
        if creator_id:
            query = query.filter(self.model.created_by_user_id == creator_id)
            
        jobs = query.offset(skip).limit(limit).all()
        return [JobResponse.from_model(job) for job in jobs]
