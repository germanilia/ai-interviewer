"""
Interview session service for handling business logic.
"""
import logging
from typing import Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.crud.interview_session import interview_session_dao
from app.crud.candidate import candidate_dao
from app.crud.interview import interview_dao
from app.crud.interview_question import InterviewQuestionDAO
from app.models.interview import QuestionImportance, InterviewQuestionStatus, Interview
from app.schemas.interview_session import (
    CandidateLoginResponse,
    InterviewSessionResponse,
    ChatResponse,
    InterviewContext
)
from app.schemas.interview import InterviewResponse
from app.services.interview_llm_service import InterviewLLMService
from app.services.question_evaluation_service import QuestionEvaluationService
from app.schemas.question import QuestionResponse

logger = logging.getLogger(__name__)


class InterviewSessionService:
    """Service for handling interview session business logic"""

    def __init__(self, llm_service: InterviewLLMService):
        self.session_dao = interview_session_dao
        self.llm_service = llm_service
        self.interview_question_dao = InterviewQuestionDAO()
        self.question_evaluation_service = QuestionEvaluationService()

    def _get_initial_message(self, interview: Union[Interview, InterviewResponse], candidate_name: str) -> str:
        """Get initial greeting message with variable substitution"""
        # Get the initial greeting value
        initial_greeting = getattr(interview, 'initial_greeting', None)
        if initial_greeting:
            try:
                # Substitute variables in the greeting
                return initial_greeting.format(
                    candidate_name=candidate_name,
                    interview_title=interview.job_title,
                    job_description=getattr(interview, 'job_description', None) or "",
                    job_department=getattr(interview, 'job_department', None) or ""
                )
            except (KeyError, ValueError) as e:
                logger.warning(f"Error formatting initial greeting: {e}. Using fallback.")
                # Fall through to fallback logic

        # Fallback to language-based default if no custom greeting or formatting error
        language = getattr(interview, 'language', 'English')
        if language == "Hebrew":
            return f"שלום {candidate_name}, איך אתה היום?"
        elif language == "Arabic":
            return f"مرحباً {candidate_name}، كيف حالك اليوم؟"
        else:  # English or default
            return f"Hello {candidate_name}, how are you today?"

    def authenticate_candidate(self, db: Session, pass_key: str) -> CandidateLoginResponse:
        """
        Authenticate candidate using pass key and return interview context.
        Creates a new session immediately upon successful login.
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

        # If no active session exists, create one immediately upon login
        if not existing_session:
            existing_session = self.session_dao.create_session(
                db=db,
                candidate_id=candidate.id,
                interview_id=candidate.interview_id
            )
            logger.info(f"Created new session {existing_session.id} for candidate {candidate.id} upon login")

            # Add initial message to conversation history based on interview greeting
            initial_message = self._get_initial_message(interview, candidate_name)
            self.session_dao.add_message_to_conversation(
                db=db,
                session_id=existing_session.id,
                role="assistant",
                content=initial_message
            )
            logger.info(f"Added initial message in {interview.language} to session {existing_session.id}")

        return CandidateLoginResponse(
            candidate_id=candidate.id,
            candidate_name=candidate_name,
            interview_id=candidate.interview_id,
            interview_title=interview.job_title,
            session_id=existing_session.id,
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

        # Add initial message to conversation history based on interview greeting
        candidate_name = f"{candidate.first_name} {candidate.last_name}"
        initial_message = self._get_initial_message(interview, candidate_name)
        self.session_dao.add_message_to_conversation(
            db=db,
            session_id=session.id,
            role="assistant",
            content=initial_message
        )
        logger.info(f"Added initial message in {interview.language} to session {session.id}")

        return session

    def process_chat_message(
        self,
        db: Session,
        session_id: int,
        user_message: str
    ) -> ChatResponse:
        """
        Process chat message with question-by-question flow.
        Language is retrieved from the interview model.
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

        # Get session to access current_question_index
        # The session object already has current_question_index from the schema
        current_index = session.current_question_index

        # Get current question based on session's current_question_index
        interview_questions = self.interview_question_dao.get_by_interview(db=db, interview_id=session.interview_id, limit=1000)
        if not interview_questions:
            raise ValueError("No questions found for this interview")

        # Sort by order_index to ensure correct sequence (already done in DAO, but keeping for clarity)
        interview_questions.sort(key=lambda x: x.order_index)

        # Check if all questions are completed
        if current_index >= len(interview_questions):
            # All questions completed, end interview
            session = self.session_dao.complete_session(db=db, session_id=session_id)
            self._update_candidate_status_on_completion(db, session.candidate_id)
            return ChatResponse(
                session_id=session_id,
                assistant_message="Thank you for completing the interview!",
                session_status=session.status,
                is_interview_complete=True
            )

        # Get current interview question
        current_interview_question = interview_questions[current_index]

        # Get the full question object
        from app.crud.question import QuestionDAO
        question_dao = QuestionDAO()
        current_question = question_dao.get(db=db, id=current_interview_question.question_id)
        if not current_question:
            raise ValueError(f"Question not found: {current_interview_question.question_id}")

        logger.info(f"Processing question {current_index + 1}/{len(interview_questions)}: {current_question.title}")

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
            # Step 1: Prepare initial context for evaluation
            logger.info(f"Preparing interview context for evaluation")
            context = self.llm_service.prepare_interview_context(
                candidate_name=candidate_name,
                interview_title=interview.job_title,
                job_description=interview.job_description,
                current_question=current_question,
                conversation_history=conversation_dict
            )

            # Step 2: Determine which question to use based on evaluation
            question_to_use, new_index = self._determine_question_to_use(
                db=db,
                context=context,
                current_question=current_question,
                current_index=current_index,
                interview_questions=interview_questions,
                user_message=user_message
            )

            # Step 3: Update context with the selected question if it changed
            if question_to_use.id != current_question.id:
                logger.info(f"Question changed from '{current_question.title}' to '{question_to_use.title}'")
                context = self.llm_service.prepare_interview_context(
                    candidate_name=candidate_name,
                    interview_title=interview.job_title,
                    job_description=interview.job_description,
                    current_question=question_to_use,
                    conversation_history=conversation_dict
                )

            # Step 4: Get LLM response using the selected question
            logger.info(f"Processing interview message with LLM service using {interview.language} language")
            llm_response = self.llm_service.process_interview_message(
                db=db,
                context=context,
                user_message=user_message,
                language=interview.language
            )
        except Exception as e:
            logger.exception(f"Error in LLM processing: {e}")
            raise
        
        # Add assistant response to conversation
        session = self.session_dao.add_message_to_conversation(
            db=db,
            session_id=session_id,
            role="assistant",
            content=llm_response.assistant_response
        )

        # Handle question progression based on evaluation results
        if new_index != current_index:
            # Question index changed, update session with new index and increment questions_asked
            from app.schemas.interview_session import InterviewSessionUpdate
            session_update = InterviewSessionUpdate(
                current_question_index=new_index,
                questions_asked=session.questions_asked + 1
            )
            # Update session using DAO - the DAO handles response object conversion internally
            session = self.session_dao.update(db=db, db_obj=session, obj_in=session_update)  # type: ignore

            # Update current question status to ANSWERED
            db_interview_question = self.interview_question_dao.get_model(db=db, id=current_interview_question.id)
            if db_interview_question:
                from app.schemas.interview_question import InterviewQuestionUpdate
                question_update = InterviewQuestionUpdate(status=InterviewQuestionStatus.ANSWERED)
                self.interview_question_dao.update(
                    db=db,
                    db_obj=db_interview_question,
                    obj_in=question_update
                )

            logger.info(f"Advanced to question {new_index + 1}/{len(interview_questions)}")
            current_index = new_index

        # Check if interview is complete (all questions processed)
        is_interview_complete = current_index >= len(interview_questions)

        if is_interview_complete:
            session = self.session_dao.complete_session(db=db, session_id=session_id)
            self._update_candidate_status_on_completion(db, session.candidate_id)
            logger.info("Interview completed - all questions processed")

        return ChatResponse(
            session_id=session_id,
            assistant_message=llm_response.assistant_response,
            session_status=session.status,
            is_interview_complete=is_interview_complete
        )

    def _determine_question_to_use(
        self,
        db: Session,
        context: InterviewContext,
        current_question: "QuestionResponse",
        current_index: int,
        interview_questions: list,
        user_message: str
    ) -> tuple["QuestionResponse", int]:
        """
        Determine which question to inject into the LLM based on evaluation results and question importance.

        Args:
            db: Database session
            context: Interview context
            current_question: The current question being evaluated
            current_index: Current question index
            interview_questions: List of all interview questions
            user_message: User's latest message

        Returns:
            Tuple of (question_to_use, new_index)
        """
        # Evaluate if the current question was answered using Claude 4
        evaluation_result = self.question_evaluation_service.evaluate_question_answered(
            db=db,
            context=context,
            current_question=current_question,
            user_message=user_message
        )

        logger.info(f"Question evaluation result: {evaluation_result.question_fully_answered}")
        logger.info(f"Evaluation reasoning: {evaluation_result.reasoning}")

        # Determine if we should proceed based on question importance and evaluation
        should_proceed = self._should_proceed_based_on_importance(
            current_question, evaluation_result.question_fully_answered
        )

        if should_proceed and current_index + 1 < len(interview_questions):
            # Move to next question
            new_index = current_index + 1
            next_question_response = interview_questions[new_index]

            # Get the full question object
            from app.crud.question import QuestionDAO
            question_dao = QuestionDAO()
            next_question = question_dao.get(db=db, id=next_question_response.question_id)
            if not next_question:
                raise ValueError(f"Next question not found: {next_question_response.question_id}")

            logger.info(f"Proceeding to next question {new_index + 1}/{len(interview_questions)}: {next_question.title}")
            return next_question, new_index
        else:
            # Stay on current question or we've reached the end
            logger.info(f"Staying on current question: {current_question.title}")
            return current_question, current_index

    def _should_proceed_based_on_importance(self, question: "QuestionResponse", fully_answered: bool) -> bool:
        """
        Determine if we should proceed to the next question based on question importance and answer status.

        Args:
            question: The current question object
            fully_answered: Whether the question was fully answered

        Returns:
            bool: True if we should move to the next question
        """
        if question.importance == QuestionImportance.MANDATORY:
            # For mandatory questions, only proceed if fully answered
            return fully_answered
        elif question.importance == QuestionImportance.ASK_ONCE:
            # For ask_once questions, proceed regardless (they require an answer, any answer)
            return True
        else:  # OPTIONAL
            # For optional questions, always proceed regardless of answer quality
            return True

    def end_session(self, db: Session, session_id: int) -> InterviewSessionResponse:
        """
        End an interview session manually and update candidate status.
        Marks all remaining questions as SKIPPED.
        """
        logger.info(f"Ending interview session {session_id}")

        # Get session to verify it exists and get candidate info
        session = self.session_dao.get(db=db, id=session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            raise ValueError("Session not found")

        logger.info(f"Found session {session_id} for candidate {session.candidate_id}")

        # Mark all remaining questions as SKIPPED
        self._mark_remaining_questions_as_skipped(db, session)

        # Complete the session
        completed_session = self.session_dao.complete_session(
            db=db,
            session_id=session_id
        )
        logger.info(f"Session {session_id} marked as completed")

        # Update candidate status to completed
        logger.info(f"About to update candidate status for candidate {session.candidate_id}")
        self._update_candidate_status_on_completion(db, session.candidate_id)
        logger.info(f"Candidate status update completed for candidate {session.candidate_id}")

        return completed_session

    def _mark_remaining_questions_as_skipped(self, db: Session, session: InterviewSessionResponse) -> None:
        """
        Mark all remaining questions (from current_question_index onwards) as SKIPPED.

        Args:
            db: Database session
            session: Interview session response object
        """
        logger.info(f"Marking remaining questions as SKIPPED for session {session.id}")

        # Get all interview questions for this interview
        interview_questions = self.interview_question_dao.get_by_interview(db=db, interview_id=session.interview_id, limit=1000)
        if not interview_questions:
            logger.warning(f"No questions found for interview {session.interview_id}")
            return

        # Sort by order_index to ensure correct sequence
        interview_questions.sort(key=lambda x: x.order_index)

        # Mark questions from current_question_index onwards as SKIPPED
        current_index = session.current_question_index
        questions_to_skip = interview_questions[current_index:]

        logger.info(f"Marking {len(questions_to_skip)} questions as SKIPPED (from index {current_index})")

        for interview_question in questions_to_skip:
            # Only skip questions that are still PENDING
            if interview_question.status == InterviewQuestionStatus.PENDING:
                db_interview_question = self.interview_question_dao.get_model(db=db, id=interview_question.id)
                if db_interview_question:
                    from app.schemas.interview_question import InterviewQuestionUpdate
                    question_update = InterviewQuestionUpdate(status=InterviewQuestionStatus.SKIPPED)
                    self.interview_question_dao.update(
                        db=db,
                        db_obj=db_interview_question,
                        obj_in=question_update
                    )
                    logger.info(f"Marked question {interview_question.id} as SKIPPED")

    def _update_candidate_status_on_completion(self, db: Session, candidate_id: int) -> None:
        """
        Update candidate status when interview session is completed
        """
        logger.info(f"Updating candidate status on completion for candidate {candidate_id}")
        from app.schemas.candidate import CandidateUpdate
        from datetime import datetime, timezone

        # Get candidate
        candidate = candidate_dao.get(db=db, id=candidate_id)
        if not candidate:
            logger.error(f"Candidate {candidate_id} not found")
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

        # Generate candidate report (don't let this fail the interview completion)
        logger.info(f"Attempting to generate report for candidate {candidate_id}")
        try:
            self._generate_candidate_report(db, candidate_id)
            logger.info(f"Report generation completed for candidate {candidate_id}")
        except Exception as e:
            logger.error(f"Failed to generate report for candidate {candidate_id}, but interview completion succeeded: {e}")

    def _generate_candidate_report(self, db: Session, candidate_id: int) -> None:
        """
        Generate an AI-powered candidate report after interview completion
        """
        logger.info(f"Starting AI report generation for candidate {candidate_id}")

        try:
            from app.services.candidate_report_service import CandidateReportService
            logger.info("Successfully imported AI report service")
        except Exception as e:
            logger.error(f"Failed to import AI report service: {e}")
            return

        # Get candidate details using DAO instance
        from app.crud.candidate import CandidateDAO
        candidate_dao_instance = CandidateDAO()
        candidate = candidate_dao_instance.get(db=db, id=candidate_id)
        if not candidate:
            logger.warning(f"Candidate {candidate_id} not found for report generation")
            return

        candidate_name = f"{candidate.first_name} {candidate.last_name}"
        logger.info(f"Generating AI report for candidate: {candidate_name}")

        try:
            # Use the AI-powered report service
            report_service = CandidateReportService()
            report_data = report_service.generate_ai_report(db=db, candidate_id=candidate_id)

            if report_data:
                logger.info(f"Successfully generated AI report for candidate {candidate_id}")
            else:
                logger.warning(f"AI report generation returned None for candidate {candidate_id}")

        except Exception as e:
            logger.exception(f"Failed to generate AI report for candidate {candidate_id}: {e}")


# Service will be created via dependency injection
