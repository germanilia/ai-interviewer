"""
Question service layer for business logic and coordination.
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.question import QuestionDAO
from app.crud.job import JobDAO
from app.crud.job_question import JobQuestionDAO
from app.schemas.question import (
    QuestionResponse, QuestionCreate, QuestionUpdate, QuestionListResponse,
    QuestionFilter, BulkQuestionDelete, BulkQuestionCategoryUpdate,
    JobQuestionAssignment
)
from app.schemas.job_question import JobQuestionCreate
from app.models.interview import QuestionCategory, QuestionImportance

logger = logging.getLogger(__name__)


class QuestionService:
    """
    Service layer for question operations.
    Handles business logic and coordinates between routers and DAOs.
    """

    def __init__(self, question_dao: QuestionDAO, job_dao: JobDAO, job_question_dao: JobQuestionDAO):
        """
        Initialize QuestionService with DAO dependencies.
        
        Args:
            question_dao: QuestionDAO instance for database operations
            job_dao: JobDAO instance for job-related operations
            job_question_dao: JobQuestionDAO instance for job-question relationships
        """
        self.question_dao = question_dao
        self.job_dao = job_dao
        self.job_question_dao = job_question_dao

    def get_question_by_id(self, db: Session, question_id: int) -> Optional[QuestionResponse]:
        """
        Get a question by ID.
        
        Args:
            db: Database session
            question_id: Question ID
            
        Returns:
            QuestionResponse if found, None otherwise
        """
        logger.info(f"Getting question by ID: {question_id}")
        return self.question_dao.get(db, question_id)

    def get_questions(
        self, 
        db: Session, 
        page: int = 1, 
        page_size: int = 10,
        filters: Optional[QuestionFilter] = None
    ) -> QuestionListResponse:
        """
        Get paginated list of questions with optional filtering.
        
        Args:
            db: Database session
            page: Page number (1-based)
            page_size: Number of items per page
            filters: Optional filtering parameters
            
        Returns:
            QuestionListResponse with paginated results
        """
        logger.info(f"Getting questions with page={page}, page_size={page_size}, filters={filters}")
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
            
        skip = (page - 1) * page_size
        
        # Get questions with filtering
        questions, total = self.question_dao.get_multi_with_filter(
            db, skip=skip, limit=page_size, filters=filters
        )
        
        # Calculate pagination info
        total_pages = (total + page_size - 1) // page_size
        
        return QuestionListResponse(
            questions=questions,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def create_question(self, db: Session, question_create: QuestionCreate) -> QuestionResponse:
        """
        Create a new question.
        
        Args:
            db: Database session
            question_create: Question creation data
            
        Returns:
            Created QuestionResponse
        """
        logger.info(f"Creating question: {question_create.title}")
        return self.question_dao.create(db, obj_in=question_create)

    def update_question(self, db: Session, question_id: int, question_update: QuestionUpdate) -> Optional[QuestionResponse]:
        """
        Update a question by ID.

        Args:
            db: Database session
            question_id: Question ID
            question_update: Question update data

        Returns:
            Updated QuestionResponse if found, None otherwise
        """
        logger.info(f"Updating question: {question_id}")

        # Check if question exists first
        existing_question = self.question_dao.get(db, question_id)
        if not existing_question:
            return None

        # Get the SQLAlchemy model for update - this should be handled by DAO
        # For now, we need to access the model directly until we enhance the DAO
        from app.models.interview import Question
        db_question = db.query(Question).filter(Question.id == question_id).first()
        if not db_question:
            return None

        return self.question_dao.update(db, db_obj=db_question, obj_in=question_update)

    def delete_question(self, db: Session, question_id: int) -> bool:
        """
        Delete a question by ID.

        Args:
            db: Database session
            question_id: Question ID

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting question: {question_id}")

        # Use DAO delete method
        return self.question_dao.delete(db, id=question_id)

    def search_questions(self, db: Session, search_term: str, page: int = 1, page_size: int = 10) -> QuestionListResponse:
        """
        Search questions by title or question text.
        
        Args:
            db: Database session
            search_term: Search term
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            QuestionListResponse with search results
        """
        logger.info(f"Searching questions with term: {search_term}")
        
        # Use filter-based search for consistency
        filters = QuestionFilter(search=search_term)
        return self.get_questions(db, page=page, page_size=page_size, filters=filters)

    def get_questions_by_category(self, db: Session, category: QuestionCategory, page: int = 1, page_size: int = 10) -> QuestionListResponse:
        """
        Get questions by category.

        Args:
            db: Database session
            category: Question category
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            QuestionListResponse with filtered results
        """
        logger.info(f"Getting questions by category: {category}")

        filters = QuestionFilter(category=category, search=None)
        return self.get_questions(db, page=page, page_size=page_size, filters=filters)

    def bulk_delete_questions(self, db: Session, bulk_delete: BulkQuestionDelete) -> int:
        """
        Delete multiple questions.
        
        Args:
            db: Database session
            bulk_delete: Bulk delete operation data
            
        Returns:
            Number of questions deleted
        """
        logger.info(f"Bulk deleting {len(bulk_delete.question_ids)} questions")
        return self.question_dao.delete_multiple(db, bulk_delete.question_ids)

    def bulk_update_category(self, db: Session, bulk_update: BulkQuestionCategoryUpdate) -> int:
        """
        Update category for multiple questions.
        
        Args:
            db: Database session
            bulk_update: Bulk category update operation data
            
        Returns:
            Number of questions updated
        """
        logger.info(f"Bulk updating category for {len(bulk_update.question_ids)} questions to {bulk_update.new_category}")
        return self.question_dao.update_category_bulk(db, bulk_update.question_ids, bulk_update.new_category)

    def assign_question_to_job(self, db: Session, assignment: JobQuestionAssignment) -> bool:
        """
        Assign a question to a job.
        
        Args:
            db: Database session
            assignment: Job question assignment data
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If question or job not found
        """
        logger.info(f"Assigning question {assignment.question_id} to job {assignment.job_id}")
        
        # Validate question exists
        question = self.question_dao.get(db, assignment.question_id)
        if not question:
            raise ValueError("Question not found")
        
        # Validate job exists
        job = self.job_dao.get(db, assignment.job_id)
        if not job:
            raise ValueError("Job not found")
        
        # Determine order index if not provided
        order_index = assignment.order_index
        if order_index is None:
            # Get the next order index for this job
            existing_assignments = self.job_question_dao.get_by_job(db, assignment.job_id)
            order_index = len(existing_assignments) + 1
        
        # Create the job question assignment
        job_question_create = JobQuestionCreate(
            job_id=assignment.job_id,
            question_id=assignment.question_id,
            order_index=order_index
        )
        
        self.job_question_dao.create(db, obj_in=job_question_create)
        return True

    def get_questions_with_creator_info(self, db: Session, page: int = 1, page_size: int = 10) -> QuestionListResponse:
        """
        Get questions with creator information.

        Args:
            db: Database session
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            QuestionListResponse with creator information
        """
        logger.info(f"Getting questions with creator info, page={page}, page_size={page_size}")

        # Validate pagination parameters
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        skip = (page - 1) * page_size

        # Get questions with creator info using DAO
        questions = self.question_dao.get_questions_with_creator_info(db, skip=skip, limit=page_size)

        # Get total count using DAO method
        all_questions = self.question_dao.get_multi(db, skip=0, limit=1000)  # Get a large number to count
        total = len(all_questions)
        total_pages = (total + page_size - 1) // page_size

        return QuestionListResponse(
            questions=questions,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
