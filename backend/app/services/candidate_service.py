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

    def get_candidate_by_pass_key(self, db: Session, pass_key: str) -> Optional[CandidateResponse]:
        """
        Get a candidate by pass key.

        Args:
            db: Database session
            pass_key: Candidate pass key

        Returns:
            CandidateResponse if found, None otherwise
        """
        logger.info(f"Getting candidate by pass key: {pass_key}")
        return self.candidate_dao.get_by_pass_key(db, pass_key)

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
            ValueError: If candidate with email already exists or interview not found
        """
        logger.info(f"Creating candidate: {candidate_create.email}")

        # Check if candidate with email already exists
        existing_candidate = self.candidate_dao.get_by_email(db, candidate_create.email)
        if existing_candidate:
            raise ValueError("Email already exists")

        # Generate pass key for interview access
        import secrets
        import string
        pass_key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        # Ensure pass key is unique
        while self.candidate_dao.get_by_pass_key(db, pass_key):
            pass_key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        # Create the candidate first
        candidate = self.candidate_dao.create(db, obj_in=candidate_create, created_by_user_id=created_by_user_id)

        # Update the candidate with the pass key using DAO
        from app.schemas.candidate import CandidateUpdate
        from app.models.candidate import Candidate

        db_candidate = db.query(Candidate).filter(Candidate.id == candidate.id).first()
        if db_candidate:
            candidate_update = CandidateUpdate(pass_key=pass_key)
            candidate = self.candidate_dao.update(db, db_obj=db_candidate, obj_in=candidate_update)

        # Update interview counter if candidate is assigned to an interview
        if candidate_create.interview_id:
            from app.models.interview import Interview
            from sqlalchemy import update, func

            # Use SQLAlchemy update statement to increment counter (handle NULL case)
            stmt = update(Interview).where(Interview.id == candidate_create.interview_id).values(
                total_candidates=func.coalesce(Interview.total_candidates, 0) + 1
            )
            result = db.execute(stmt)
            db.commit()

            if result.rowcount > 0:
                logger.info(f"Updated interview {candidate_create.interview_id} total_candidates")
            else:
                logger.warning(f"Interview {candidate_create.interview_id} not found when creating candidate")

        return candidate

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

    def reset_candidate_interview(self, db: Session, candidate_id: int) -> Optional[CandidateResponse]:
        """
        Reset candidate interview status and date.
        This removes the interview status and interview date, allowing the candidate to retake the interview.

        Args:
            db: Database session
            candidate_id: Candidate ID

        Returns:
            Updated CandidateResponse if found, None otherwise
        """
        logger.info(f"Resetting interview for candidate: {candidate_id}")

        # Check if candidate exists
        existing_candidate = self.candidate_dao.get(db, candidate_id)
        if not existing_candidate:
            return None

        # Create update object to reset interview fields
        reset_update = CandidateUpdate(
            interview_status=None,
            interview_date=None,
            completed_at=None,
            score=None,
            integrity_score=None,
            risk_level=None,
            conversation=None,
            report_summary=None,
            risk_indicators=None,
            key_concerns=None,
            analysis_notes=None
        )

        return self.candidate_dao.update_by_id(db, candidate_id, reset_update)
