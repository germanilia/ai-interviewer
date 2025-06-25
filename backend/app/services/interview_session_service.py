"""
Interview session service for handling business logic.
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.crud.interview_session import interview_session_dao
from app.crud.candidate import candidate_dao
from app.crud.interview import interview_dao
from app.schemas.interview_session import (
    CandidateLoginResponse,
    InterviewSessionResponse,
    ChatResponse
)
from app.services.interview_llm_service import interview_llm_service

logger = logging.getLogger(__name__)


class InterviewSessionService:
    """Service for handling interview session business logic"""

    def __init__(self):
        self.session_dao = interview_session_dao
        self.llm_service = interview_llm_service

    def authenticate_candidate(self, db: Session, pass_key: str) -> CandidateLoginResponse:
        """
        Authenticate candidate using pass key and return interview context
        """
        # Find candidate by pass key
        candidate = candidate_dao.get_by_pass_key(db=db, pass_key=pass_key)

        if not candidate:
            raise ValueError("Invalid pass key")

        if not candidate.interview_id:
            raise ValueError("Candidate is not assigned to an interview")

        # Get interview details
        interview = interview_dao.get(db=db, id=candidate.interview_id)

        if not interview:
            raise ValueError("Interview not found")

        # Check for existing active session
        existing_session = self.session_dao.get_active_session(
            db=db,
            candidate_id=candidate.id,
            interview_id=candidate.interview_id
        )

        candidate_name = f"{candidate.first_name} {candidate.last_name}"

        return CandidateLoginResponse(
            candidate_id=candidate.id,
            candidate_name=candidate_name,
            interview_id=candidate.interview_id,
            interview_title=interview.job_title,
            session_id=existing_session.id if existing_session else None,
            message=f"Welcome {candidate_name}! You are logged in for the {interview.job_title} interview."
        )

    def start_session(self, db: Session, candidate_id: int, interview_id: int) -> InterviewSessionResponse:
        """
        Start a new interview session for a candidate
        """
        # Verify candidate and interview exist
        candidate = candidate_dao.get(db=db, id=candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        interview = interview_dao.get(db=db, id=interview_id)
        if not interview:
            raise ValueError("Interview not found")

        # Check if there's already an active session
        existing_session = self.session_dao.get_active_session(
            db=db,
            candidate_id=candidate_id,
            interview_id=interview_id
        )

        if existing_session:
            return existing_session

        # Create new session
        session = self.session_dao.create_session(
            db=db,
            candidate_id=candidate_id,
            interview_id=interview_id
        )

        return session

    def process_chat_message(
        self,
        db: Session,
        session_id: int,
        user_message: str,
        language: str = "en"
    ) -> ChatResponse:
        """
        Process chat message and return LLM response
        """
        # Get session
        session = self.session_dao.get(db=db, id=session_id)
        if not session:
            raise ValueError("Session not found")
        
        # Get candidate and interview details
        candidate = candidate_dao.get(db=db, id=session.candidate_id)
        interview = interview_dao.get(db=db, id=session.interview_id)

        if not candidate or not interview:
            raise ValueError("Candidate or interview not found")

        # Add user message to conversation
        session = self.session_dao.add_message_to_conversation(
            db=db,
            session_id=session_id,
            role="user",
            content=user_message
        )

        # Prepare context for LLM
        candidate_name = f"{candidate.first_name} {candidate.last_name}"

        # Get interview questions - need to get the model to access questions
        interview_model = interview_dao.get_model(db=db, id=session.interview_id)
        questions = []
        if interview_model:
            logger.info(f"Found interview model with {len(interview_model.interview_questions)} interview questions")
            from app.crud.question import QuestionDAO
            question_dao = QuestionDAO()
            for iq in interview_model.interview_questions:
                logger.info(f"Processing interview question {iq.id} with question_id {iq.question_id}")
                # Get the full question object from the database
                question = question_dao.get(db=db, id=iq.question_id)
                if question:
                    logger.info(f"Retrieved question: {question.title}")
                    questions.append(question)
                else:
                    logger.warning(f"Could not retrieve question with ID {iq.question_id}")
        else:
            logger.warning(f"No interview model found for interview_id {session.interview_id}")

        # Convert conversation history to dict format for LLM
        conversation_dict = []
        if session.conversation_history:
            for msg in session.conversation_history:
                conversation_dict.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "question_id": msg.question_id
                })

        try:
            logger.info(f"Preparing interview context with {len(questions)} questions")
            context = self.llm_service.prepare_interview_context(
                candidate_name=candidate_name,
                interview_title=interview.job_title,
                job_description=interview.job_description,
                questions=questions,
                conversation_history=conversation_dict
            )

            # Get LLM response
            logger.info("Processing interview message with LLM service")
            assistant_response, is_complete = self.llm_service.process_interview_message(
                context=context,
                user_message=user_message,
                language=language
            )
        except Exception as e:
            logger.exception(f"Error in LLM processing: {e}")
            raise
        
        # Add assistant response to conversation
        session = self.session_dao.add_message_to_conversation(
            db=db,
            session_id=session_id,
            role="assistant",
            content=assistant_response
        )
        
        # Complete session if interview is done
        if is_complete:
            session = self.session_dao.complete_session(
                db=db,
                session_id=session_id
            )
            # Update candidate status to completed
            self._update_candidate_status_on_completion(db, session.candidate_id)

        return ChatResponse(
            session_id=session_id,
            assistant_message=assistant_response,
            session_status=session.status,
            is_interview_complete=is_complete
        )

    def end_session(self, db: Session, session_id: int) -> InterviewSessionResponse:
        """
        End an interview session manually and update candidate status
        """
        # Get session to verify it exists and get candidate info
        session = self.session_dao.get(db=db, id=session_id)
        if not session:
            raise ValueError("Session not found")

        # Complete the session
        completed_session = self.session_dao.complete_session(
            db=db,
            session_id=session_id
        )

        # Update candidate status to completed
        self._update_candidate_status_on_completion(db, session.candidate_id)

        return completed_session

    def _update_candidate_status_on_completion(self, db: Session, candidate_id: int) -> None:
        """
        Update candidate status when interview session is completed
        """
        from app.schemas.candidate import CandidateUpdate
        from datetime import datetime, timezone

        # Get candidate
        candidate = candidate_dao.get(db=db, id=candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        # Update candidate status to completed with interview date
        completion_time = datetime.now(timezone.utc)
        update_data = CandidateUpdate(
            interview_status="completed",
            interview_date=completion_time,
            completed_at=completion_time
        )

        # Get the actual database object for update
        db_candidate = db.query(candidate_dao.model).filter(candidate_dao.model.id == candidate_id).first()
        if db_candidate:
            candidate_dao.update(db=db, db_obj=db_candidate, obj_in=update_data)


# Create instance for dependency injection
interview_session_service = InterviewSessionService()
