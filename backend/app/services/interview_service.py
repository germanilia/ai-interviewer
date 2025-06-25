"""
Interview service layer for business logic.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.interview import InterviewDAO
from app.crud.candidate import CandidateDAO
from app.crud.interview_question import InterviewQuestionDAO
from app.crud.question import QuestionDAO

from app.schemas.interview import (
    InterviewResponse,
    InterviewCreate,
    InterviewUpdate,
    InterviewListResponse,
    InterviewWithDetails
)
from app.schemas.interview_question import InterviewQuestionCreate
from app.core.logging_service import get_logger

logger = get_logger(__name__)


class InterviewService:
    """
    Service layer for interview operations.
    Handles business logic and coordinates between routers and DAOs.
    """

    def __init__(self, interview_dao: InterviewDAO, candidate_dao: CandidateDAO,
                 interview_question_dao: InterviewQuestionDAO, question_dao: QuestionDAO):
        """
        Initialize InterviewService with DAO dependencies.

        Args:
            interview_dao: InterviewDAO instance for database operations
            candidate_dao: CandidateDAO instance for candidate operations
            interview_question_dao: InterviewQuestionDAO instance for interview question operations
            question_dao: QuestionDAO instance for question operations
        """
        self.interview_dao = interview_dao
        self.candidate_dao = candidate_dao
        self.interview_question_dao = interview_question_dao
        self.question_dao = question_dao

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
        candidate_id: Optional[int] = None
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
            
        Returns:
            InterviewListResponse with paginated results
        """
        logger.info(f"Getting interviews with page={page}, page_size={page_size}, status={status}, search={search}")

        interviews, total = self.interview_dao.get_interviews_paginated(
            db,
            page=page,
            page_size=page_size,
            search=search,
            candidate_id=candidate_id,
        )

        # Convert to response objects with details
        interview_items = []
        for interview in interviews:
            # Get assigned candidates for this interview
            from app.models.candidate import Candidate
            candidates = db.query(Candidate).filter(Candidate.interview_id == interview.id).all()

            # Get questions for this interview
            from app.models.interview import InterviewQuestion, Question
            questions = db.query(Question).join(InterviewQuestion).filter(
                InterviewQuestion.interview_id == interview.id
            ).order_by(InterviewQuestion.order_index).all()

            interview_detail = InterviewWithDetails.from_model_with_details(
                interview, candidates=candidates, questions=questions
            )
            interview_items.append(interview_detail)
        
        # Get status counts for tabs
        status_counts = self.interview_dao.get_status_counts(
            db, candidate_id=candidate_id, search=search
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
        Create a new interview with required questions.

        Args:
            db: Database session
            interview_create: Interview creation data
            created_by_user_id: ID of the user creating the interview

        Returns:
            Created InterviewResponse

        Raises:
            ValueError: If candidate or questions not found
        """

        # Validate all questions exist (questions are now required)
        valid_questions = []
        for question_id in interview_create.question_ids:
            question = self.question_dao.get(db, question_id)
            if not question:
                raise ValueError(f"Question with ID {question_id} not found")
            valid_questions.append(question)

        # Create the interview
        interview = self.interview_dao.create(db, obj_in=interview_create, created_by_user_id=created_by_user_id)

        # Create interview questions (now guaranteed to have questions)
        logger.info(f"Creating {len(interview_create.question_ids)} interview questions")
        for index, (question_id, question) in enumerate(zip(interview_create.question_ids, valid_questions)):
            interview_question_create = InterviewQuestionCreate(
                interview_id=interview.id,
                question_id=question_id,
                order_index=index + 1,
                question_text_snapshot=question.question_text
            )
            self.interview_question_dao.create(db, obj_in=interview_question_create)

        return interview

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

    def update_interview_questions(self, db: Session, interview_id: int, question_ids: list[int]) -> Optional[InterviewResponse]:
        """
        Update the questions assigned to an interview.
        This will replace all existing questions with the new list.

        Args:
            db: Database session
            interview_id: Interview ID
            question_ids: List of question IDs to assign

        Returns:
            Updated InterviewResponse if found, None otherwise

        Raises:
            ValueError: If any question not found
        """
        logger.info(f"Updating questions for interview {interview_id}: {question_ids}")

        # Check if interview exists
        interview = self.interview_dao.get_model(db, interview_id)
        if not interview:
            return None

        # Validate all questions exist
        valid_questions = []
        for question_id in question_ids:
            question = self.question_dao.get(db, question_id)
            if not question:
                raise ValueError(f"Question with ID {question_id} not found")
            valid_questions.append(question)

        # Delete existing interview questions
        from app.models.interview import InterviewQuestion
        db.query(InterviewQuestion).filter(InterviewQuestion.interview_id == interview_id).delete()

        # Create new interview questions
        for index, (question_id, question) in enumerate(zip(question_ids, valid_questions)):
            interview_question_create = InterviewQuestionCreate(
                interview_id=interview_id,
                question_id=question_id,
                order_index=index + 1,
                question_text_snapshot=question.question_text
            )
            self.interview_question_dao.create(db, obj_in=interview_question_create)

        db.commit()

        # Return updated interview
        return self.interview_dao.get(db, interview_id)


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


