"""
Candidate service layer for business logic.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.candidate import CandidateDAO
from app.schemas.candidate import (
    CandidateResponse, 
    CandidateCreate, 
    CandidateUpdate, 
    CandidateListResponse
)
from app.core.logging_service import get_logger

logger = get_logger(__name__)


class CandidateService:
    """
    Service layer for candidate operations.
    Handles business logic and coordinates between routers and DAOs.
    """

    def __init__(self, candidate_dao: CandidateDAO):
        """
        Initialize CandidateService with CandidateDAO dependency.
        
        Args:
            candidate_dao: CandidateDAO instance for database operations
        """
        self.candidate_dao = candidate_dao

    def get_candidate_by_id(self, db: Session, candidate_id: int) -> Optional[CandidateResponse]:
        """
        Get a candidate by ID.
        
        Args:
            db: Database session
            candidate_id: Candidate ID
            
        Returns:
            CandidateResponse if found, None otherwise
        """
        logger.info(f"Getting candidate by ID: {candidate_id}")
        return self.candidate_dao.get(db, candidate_id)

    def get_candidates(
        self, 
        db: Session, 
        page: int = 1, 
        page_size: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> CandidateListResponse:
        """
        Get candidates with pagination, search, and filtering.
        
        Args:
            db: Database session
            page: Page number (1-based)
            page_size: Number of items per page
            search: Search term for name/email
            status: Status filter
            
        Returns:
            CandidateListResponse with paginated results
        """
        logger.info(f"Getting candidates with page={page}, page_size={page_size}, search={search}, status={status}")
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
            
        skip = (page - 1) * page_size
        
        candidates, total = self.candidate_dao.get_multi_with_search(
            db, 
            skip=skip, 
            limit=page_size,
            search=search,
            status=status
        )
        
        return CandidateListResponse.create(
            items=candidates,
            total=total,
            page=page,
            page_size=page_size
        )

    def get_candidate_by_email(self, db: Session, email: str) -> Optional[CandidateResponse]:
        """
        Get a candidate by email address.
        
        Args:
            db: Database session
            email: Candidate email address
            
        Returns:
            CandidateResponse if found, None otherwise
        """
        logger.info(f"Getting candidate by email: {email}")
        return self.candidate_dao.get_by_email(db, email)

    def create_candidate(self, db: Session, candidate_create: CandidateCreate, created_by_user_id: int) -> CandidateResponse:
        """
        Create a new candidate.

        Args:
            db: Database session
            candidate_create: Candidate creation data
            created_by_user_id: ID of the user creating the candidate

        Returns:
            Created CandidateResponse

        Raises:
            ValueError: If candidate with email already exists
        """
        logger.info(f"Creating candidate: {candidate_create.email}")

        # Check if candidate with email already exists
        existing_candidate = self.candidate_dao.get_by_email(db, candidate_create.email)
        if existing_candidate:
            raise ValueError("Email already exists")

        return self.candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=created_by_user_id)

    def update_candidate(self, db: Session, candidate_id: int, candidate_update: CandidateUpdate) -> Optional[CandidateResponse]:
        """
        Update a candidate by ID.

        Args:
            db: Database session
            candidate_id: Candidate ID
            candidate_update: Candidate update data

        Returns:
            Updated CandidateResponse if found, None otherwise

        Raises:
            ValueError: If email already exists for another candidate
        """
        logger.info(f"Updating candidate: {candidate_id}")

        # First check if candidate exists
        existing_candidate = self.candidate_dao.get(db, candidate_id)
        if not existing_candidate:
            return None

        # If email is being updated, check for duplicates
        if candidate_update.email:
            candidate_with_email = self.candidate_dao.get_by_email(db, candidate_update.email)
            if candidate_with_email and candidate_with_email.id != candidate_id:
                raise ValueError("Email already exists")

        return self.candidate_dao.update_by_id(db, candidate_id, candidate_update)

    def delete_candidate(self, db: Session, candidate_id: int) -> bool:
        """
        Delete a candidate by ID.
        
        Args:
            db: Database session
            candidate_id: Candidate ID
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting candidate: {candidate_id}")
        return self.candidate_dao.delete(db, id=candidate_id)

    def get_candidate_interview_history(self, db: Session, candidate_id: int) -> List:
        """
        Get interview history for a candidate.
        
        Args:
            db: Database session
            candidate_id: Candidate ID
            
        Returns:
            List of interview records
        """
        logger.info(f"Getting interview history for candidate: {candidate_id}")
        return self.candidate_dao.get_interview_history(db, candidate_id)
