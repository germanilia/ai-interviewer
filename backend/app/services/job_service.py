"""
Job service layer for business logic and coordination.
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.job import JobDAO
from app.crud.job_question import JobQuestionDAO
from app.schemas.job import (
    JobResponse, JobCreate, JobUpdate, JobListResponse, JobFilter,
    JobStatistics, JobCloneRequest, JobWithQuestions
)

logger = logging.getLogger(__name__)


class JobService:
    """Service layer for job management operations."""

    def __init__(self, job_dao: JobDAO, job_question_dao: JobQuestionDAO):
        self.job_dao = job_dao
        self.job_question_dao = job_question_dao

    def get_jobs(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[JobFilter] = None
    ) -> JobListResponse:
        """
        Get jobs with pagination and filtering.
        
        Args:
            db: Database session
            page: Page number (1-based)
            page_size: Number of items per page
            filters: Optional filters to apply
            
        Returns:
            JobListResponse with paginated results
        """
        logger.info(f"Getting jobs - page: {page}, page_size: {page_size}")
        
        skip = (page - 1) * page_size
        
        # Apply filters if provided
        filter_kwargs = {}
        if filters:
            if filters.search:
                filter_kwargs["search"] = filters.search
            if filters.department:
                filter_kwargs["department"] = filters.department
            if filters.created_by_user_id:
                filter_kwargs["creator_id"] = filters.created_by_user_id
        
        # Get jobs and total count
        jobs = self.job_dao.get_by_filters(
            db, skip=skip, limit=page_size, **filter_kwargs
        )
        total = self.job_dao.count_by_filters(db, **filter_kwargs)
        
        # Calculate pagination info
        total_pages = (total + page_size - 1) // page_size
        
        return JobListResponse(
            jobs=jobs,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def create_job(self, db: Session, job_create: JobCreate) -> JobResponse:
        """
        Create a new job.
        
        Args:
            db: Database session
            job_create: Job creation data
            
        Returns:
            Created JobResponse
        """
        logger.info(f"Creating job: {job_create.title}")
        return self.job_dao.create(db, obj_in=job_create)

    def get_job(self, db: Session, job_id: int) -> Optional[JobResponse]:
        """
        Get a job by ID.
        
        Args:
            db: Database session
            job_id: Job ID
            
        Returns:
            JobResponse if found, None otherwise
        """
        logger.info(f"Getting job: {job_id}")
        return self.job_dao.get(db, job_id)

    def get_job_with_questions(self, db: Session, job_id: int) -> Optional[JobWithQuestions]:
        """
        Get a job with its question template.
        
        Args:
            db: Database session
            job_id: Job ID
            
        Returns:
            JobWithQuestions if found, None otherwise
        """
        logger.info(f"Getting job with questions: {job_id}")
        return self.job_dao.get_with_questions(db, job_id)

    def update_job(self, db: Session, job_id: int, job_update: JobUpdate) -> Optional[JobResponse]:
        """
        Update an existing job.
        
        Args:
            db: Database session
            job_id: Job ID
            job_update: Job update data
            
        Returns:
            Updated JobResponse if found, None otherwise
        """
        logger.info(f"Updating job: {job_id}")
        
        # Get existing job
        existing_job = db.query(self.job_dao.model).filter(
            self.job_dao.model.id == job_id
        ).first()
        
        if not existing_job:
            return None
        
        return self.job_dao.update(db, db_obj=existing_job, obj_in=job_update)

    def delete_job(self, db: Session, job_id: int) -> bool:
        """
        Delete a job.
        
        Args:
            db: Database session
            job_id: Job ID
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting job: {job_id}")
        return self.job_dao.delete(db, id=job_id)

    def get_job_statistics(self, db: Session, job_id: int) -> Optional[JobStatistics]:
        """
        Get statistics for a job.
        
        Args:
            db: Database session
            job_id: Job ID
            
        Returns:
            JobStatistics if job found, None otherwise
        """
        logger.info(f"Getting statistics for job: {job_id}")
        return self.job_dao.get_statistics(db, job_id)

    def clone_job_template(self, db: Session, clone_request: JobCloneRequest) -> bool:
        """
        Clone question template from one job to another.
        
        Args:
            db: Database session
            clone_request: Clone request data
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Cloning template from job {clone_request.source_job_id} to {clone_request.target_job_id}")
        
        if not clone_request.clone_questions:
            logger.info("Clone questions is False, skipping template clone")
            return True
        
        return self.job_dao.clone_template(
            db, clone_request.source_job_id, clone_request.target_job_id
        )

    def get_departments(self, db: Session) -> List[str]:
        """
        Get list of unique departments.
        
        Args:
            db: Database session
            
        Returns:
            List of department names
        """
        logger.info("Getting unique departments")
        return self.job_dao.get_unique_departments(db)

    def search_jobs(self, db: Session, search_term: str, page: int = 1, page_size: int = 10) -> JobListResponse:
        """
        Search jobs by title.
        
        Args:
            db: Database session
            search_term: Search term
            page: Page number
            page_size: Page size
            
        Returns:
            JobListResponse with search results
        """
        logger.info(f"Searching jobs with term: {search_term}")
        
        filters = JobFilter(search=search_term)
        return self.get_jobs(db, page=page, page_size=page_size, filters=filters)
