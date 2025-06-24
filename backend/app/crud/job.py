"""
Job DAO for database operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from app.crud.base import BaseDAO
from app.models.interview import Job, Interview, JobQuestion, InterviewStatus
from app.schemas.job import JobResponse, JobCreate, JobUpdate, JobWithQuestions, JobStatistics


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
                      creator_id: Optional[int] = None, search: Optional[str] = None,
                      skip: int = 0, limit: int = 100) -> List[JobResponse]:
        """Get jobs with multiple filters."""
        query = db.query(self.model)

        if department:
            query = query.filter(self.model.department == department)
        if creator_id:
            query = query.filter(self.model.created_by_user_id == creator_id)
        if search:
            query = query.filter(self.model.title.ilike(f"%{search}%"))

        jobs = query.offset(skip).limit(limit).all()
        return [JobResponse.from_model(job) for job in jobs]

    def count_by_filters(self, db: Session, *, department: Optional[str] = None,
                        creator_id: Optional[int] = None, search: Optional[str] = None) -> int:
        """Count jobs with multiple filters."""
        query = db.query(self.model)

        if department:
            query = query.filter(self.model.department == department)
        if creator_id:
            query = query.filter(self.model.created_by_user_id == creator_id)
        if search:
            query = query.filter(self.model.title.ilike(f"%{search}%"))

        return query.count()

    def get_statistics(self, db: Session, job_id: int) -> Optional[JobStatistics]:
        """Get statistics for a specific job."""
        job = db.query(self.model).filter(self.model.id == job_id).first()
        if not job:
            return None

        # Count questions assigned to this job
        questions_count = db.query(JobQuestion).filter(JobQuestion.job_id == job_id).count()

        # Get interview statistics
        interviews = db.query(Interview).filter(Interview.job_id == job_id).all()
        total_interviews = len(interviews)

        if total_interviews == 0:
            return JobStatistics(
                total_interviews=0,
                avg_score=None,
                completion_rate=0.0,
                avg_completion_time=None,
                questions_count=questions_count
            )

        # Calculate completion rate (completed interviews / total interviews)
        completed_interviews = [i for i in interviews if i.status.value == InterviewStatus.COMPLETED.value]
        completion_rate = len(completed_interviews) / total_interviews * 100

        # Calculate average score for completed interviews
        scores = []
        for interview in completed_interviews:
            if interview.score is not None:
                scores.append(interview.score)

        if scores:
            avg_score = sum(scores) / len(scores)
        else:
            avg_score = None

        # Calculate average completion time (placeholder - would need actual timing data)
        avg_completion_time = None  # TODO: Implement when timing data is available

        return JobStatistics(
            total_interviews=total_interviews,
            avg_score=avg_score,
            completion_rate=completion_rate,
            avg_completion_time=avg_completion_time,
            questions_count=questions_count
        )

    def clone_template(self, db: Session, source_job_id: int, target_job_id: int) -> bool:
        """Clone question template from source job to target job."""
        # Verify both jobs exist
        source_job = db.query(self.model).filter(self.model.id == source_job_id).first()
        target_job = db.query(self.model).filter(self.model.id == target_job_id).first()

        if not source_job or not target_job:
            return False

        # Get source job questions
        source_questions = db.query(JobQuestion).filter(JobQuestion.job_id == source_job_id).all()

        # Clear existing questions from target job
        db.query(JobQuestion).filter(JobQuestion.job_id == target_job_id).delete()

        # Clone questions to target job
        for source_question in source_questions:
            new_job_question = JobQuestion(
                job_id=target_job_id,
                question_id=source_question.question_id,
                order_index=source_question.order_index
            )
            db.add(new_job_question)

        db.commit()
        return True

    def get_unique_departments(self, db: Session) -> List[str]:
        """Get list of unique departments."""
        departments = db.query(self.model.department).filter(
            self.model.department.isnot(None)
        ).distinct().all()
        return [dept[0] for dept in departments if dept[0]]
