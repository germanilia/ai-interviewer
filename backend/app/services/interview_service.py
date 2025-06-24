"""
Interview service layer for business logic.
"""
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.crud.interview import InterviewDAO
from app.crud.candidate import CandidateDAO
from app.crud.job import JobDAO
from app.models.interview import InterviewStatus
from app.schemas.interview import (
    InterviewResponse, 
    InterviewCreate, 
    InterviewUpdate, 
    InterviewListResponse,
    InterviewWithDetails
)
from app.core.logging_service import get_logger

logger = get_logger(__name__)


class InterviewService:
    """
    Service layer for interview operations.
    Handles business logic and coordinates between routers and DAOs.
    """

    def __init__(self, interview_dao: InterviewDAO, candidate_dao: CandidateDAO, job_dao: JobDAO):
        """
        Initialize InterviewService with DAO dependencies.
        
        Args:
            interview_dao: InterviewDAO instance for database operations
            candidate_dao: CandidateDAO instance for candidate operations
            job_dao: JobDAO instance for job operations
        """
        self.interview_dao = interview_dao
        self.candidate_dao = candidate_dao
        self.job_dao = job_dao

    def get_interview_by_id(self, db: Session, interview_id: int) -> Optional[InterviewResponse]:
        """
        Get an interview by ID.
        
        Args:
            db: Database session
            interview_id: Interview ID
            
        Returns:
            InterviewResponse if found, None otherwise
        """
        logger.info(f"Getting interview by ID: {interview_id}")
        return self.interview_dao.get(db, interview_id)

    def get_interviews(
        self, 
        db: Session, 
        page: int = 1, 
        page_size: int = 10,
        status: Optional[str] = None,
        search: Optional[str] = None,
        candidate_id: Optional[int] = None,
        job_id: Optional[int] = None
    ) -> InterviewListResponse:
        """
        Get interviews with pagination, search, and filtering.
        
        Args:
            db: Database session
            page: Page number (1-based)
            page_size: Number of items per page
            status: Status filter
            search: Search term for candidate name
            candidate_id: Filter by candidate ID
            job_id: Filter by job ID
            
        Returns:
            InterviewListResponse with paginated results
        """
        logger.info(f"Getting interviews with page={page}, page_size={page_size}, status={status}, search={search}")

        interviews, total = self.interview_dao.get_interviews_paginated(
            db,
            page=page,
            page_size=page_size,
            status=status,
            search=search,
            candidate_id=candidate_id,
            job_id=job_id,
        )

        # Convert to response objects with details
        interview_items = [
            InterviewWithDetails.from_model_with_details(interview) 
            for interview in interviews
        ]
        
        # Get status counts for tabs
        status_counts = self.interview_dao.get_status_counts(
            db, candidate_id=candidate_id, job_id=job_id, search=search
        )
        
        return InterviewListResponse.create(
            items=interview_items,
            total=total,
            page=page,
            page_size=page_size,
            status_counts=status_counts
        )

    def create_interview(self, db: Session, interview_create: InterviewCreate, created_by_user_id: int) -> InterviewResponse:
        """
        Create a new interview.

        Args:
            db: Database session
            interview_create: Interview creation data
            created_by_user_id: ID of the user creating the interview

        Returns:
            Created InterviewResponse

        Raises:
            ValueError: If candidate or job not found
        """
        logger.info(f"Creating interview for candidate {interview_create.candidate_id}, job {interview_create.job_id}")

        # Validate candidate exists
        candidate = self.candidate_dao.get(db, interview_create.candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        # Validate job exists
        job = self.job_dao.get(db, interview_create.job_id)
        if not job:
            raise ValueError("Job not found")

        return self.interview_dao.create(db, obj_in=interview_create, created_by_user_id=created_by_user_id)

    def update_interview(self, db: Session, interview_id: int, interview_update: InterviewUpdate) -> Optional[InterviewResponse]:
        """
        Update an interview by ID.

        Args:
            db: Database session
            interview_id: Interview ID
            interview_update: Interview update data

        Returns:
            Updated InterviewResponse if found, None otherwise
        """
        logger.info(f"Updating interview: {interview_id}")

        # Get the SQLAlchemy model for update
        db_interview = self.interview_dao.get_model(db, interview_id)
        if not db_interview:
            return None

        return self.interview_dao.update(db, db_obj=db_interview, obj_in=interview_update)

    def change_interview_status(
        self, 
        db: Session, 
        interview_id: int, 
        new_status: InterviewStatus,
        reason: Optional[str] = None
    ) -> Optional[InterviewResponse]:
        """
        Change interview status.
        
        Args:
            db: Database session
            interview_id: Interview ID
            new_status: New status to set
            reason: Optional reason for status change
            
        Returns:
            Updated InterviewResponse if found, None otherwise
        """
        logger.info(f"Changing interview {interview_id} status to {new_status}")
        
        interview_update = InterviewUpdate(
            status=new_status,
            analysis_notes=reason if reason else None
        )
        
        return self.update_interview(db, interview_id, interview_update)

    def cancel_interview(self, db: Session, interview_id: int, reason: str) -> Optional[InterviewResponse]:
        """
        Cancel an interview.
        
        Args:
            db: Database session
            interview_id: Interview ID
            reason: Cancellation reason
            
        Returns:
            Updated InterviewResponse if found, None otherwise
        """
        logger.info(f"Cancelling interview: {interview_id}")
        
        return self.change_interview_status(
            db, 
            interview_id, 
            InterviewStatus.CANCELLED, 
            f"Cancelled: {reason}"
        )

    def delete_interview(self, db: Session, interview_id: int) -> bool:
        """
        Delete an interview by ID.
        
        Args:
            db: Database session
            interview_id: Interview ID
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting interview: {interview_id}")
        return self.interview_dao.delete(db, id=interview_id)


