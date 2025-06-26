"""
Interview session router for candidate authentication and chat functionality.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from app.dependencies import get_db, get_interview_session_service
from app.schemas.interview_session import (
    CandidateLoginRequest,
    CandidateLoginResponse,
    ChatRequest,
    ChatResponse,
    InterviewSessionResponse
)
from app.services.interview_session_service import InterviewSessionService

logger = logging.getLogger(__name__)

interview_session_router = APIRouter(prefix="/api/v1/interview-session", tags=["interview-session"])


@interview_session_router.post("/candidate-login", response_model=CandidateLoginResponse)
async def candidate_login(
    request: CandidateLoginRequest,
    db: Session = Depends(get_db),
    session_service: InterviewSessionService = Depends(get_interview_session_service)
):
    """
    Authenticate candidate using pass key and return interview context
    """
    try:
        return session_service.authenticate_candidate(
            db=db,
            pass_key=request.pass_key
        )

    except ValueError as e:
        logger.warning(f"Candidate login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error during candidate login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


class StartSessionRequest(BaseModel):
    candidate_id: int
    interview_id: int


@interview_session_router.post("/start-session", response_model=InterviewSessionResponse)
async def start_interview_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db),
    session_service: InterviewSessionService = Depends(get_interview_session_service)
):
    """
    Start a new interview session for a candidate
    """
    try:
        return session_service.start_session(
            db=db,
            candidate_id=request.candidate_id,
            interview_id=request.interview_id
        )

    except ValueError as e:
        logger.warning(f"Failed to start session: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error starting interview session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start session"
        )


@interview_session_router.post("/chat", response_model=ChatResponse)
async def chat_with_llm(
    request: ChatRequest,
    db: Session = Depends(get_db),
    session_service: InterviewSessionService = Depends(get_interview_session_service)
):
    """
    Process chat message and return LLM response
    """
    try:
        return session_service.process_chat_message(
            db=db,
            session_id=request.session_id,
            user_message=request.message,
            language=request.language or "en"
        )

    except ValueError as e:
        logger.warning(f"Chat processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error processing chat message")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


class EndSessionRequest(BaseModel):
    session_id: int


@interview_session_router.post("/end-session", response_model=InterviewSessionResponse)
async def end_interview_session(
    request: EndSessionRequest,
    db: Session = Depends(get_db),
    session_service: InterviewSessionService = Depends(get_interview_session_service)
):
    """
    End an interview session and update candidate status
    """
    try:
        return session_service.end_session(
            db=db,
            session_id=request.session_id
        )

    except ValueError as e:
        logger.warning(f"Failed to end session: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error ending interview session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end session"
        )
