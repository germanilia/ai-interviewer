"""
Candidate router for CRUD operations on candidates.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.candidate import CandidateResponse, CandidateCreate, CandidateUpdate, CandidateListResponse
from app.services.candidate_service import CandidateService
from app.dependencies import get_db, get_candidate_service, get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.candidate_report import CandidateReportResponse

candidate_router = APIRouter()


@candidate_router.get("/candidates", response_model=CandidateListResponse)
async def get_candidates(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search term for name or email"),
    candidate_status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    candidate_service: CandidateService = Depends(get_candidate_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get candidates with pagination, search, and filtering.
    """
    try:
        return candidate_service.get_candidates(
            db=db,
            page=page,
            page_size=page_size,
            search=search,
            status=candidate_status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve candidates: {str(e)}"
        )


@candidate_router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: Session = Depends(get_db),
    candidate_service: CandidateService = Depends(get_candidate_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create a new candidate.
    """
    try:
        return candidate_service.create_candidate(db=db, candidate_create=candidate_data, created_by_user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create candidate: {str(e)}"
        )


@candidate_router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    candidate_service: CandidateService = Depends(get_candidate_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get a specific candidate by ID.
    """
    candidate = candidate_service.get_candidate_by_id(db=db, candidate_id=candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return candidate


@candidate_router.put("/candidates/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    db: Session = Depends(get_db),
    candidate_service: CandidateService = Depends(get_candidate_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update a candidate.
    """
    try:
        updated_candidate = candidate_service.update_candidate(
            db=db,
            candidate_id=candidate_id,
            candidate_update=candidate_data
        )
        if not updated_candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        return updated_candidate
    except HTTPException:
        # Re-raise HTTPExceptions as-is (like 404 not found)
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update candidate: {str(e)}"
        )


@candidate_router.delete("/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    candidate_service: CandidateService = Depends(get_candidate_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete a candidate.
    """
    success = candidate_service.delete_candidate(db=db, candidate_id=candidate_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )


@candidate_router.get("/candidates/{candidate_id}/interviews")
async def get_candidate_interviews(
    candidate_id: int,
    db: Session = Depends(get_db),
    candidate_service: CandidateService = Depends(get_candidate_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get interview history for a specific candidate.
    """
    candidate = candidate_service.get_candidate_by_id(db=db, candidate_id=candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Get interview history using the service method
    interviews = candidate_service.get_candidate_interview_history(db=db, candidate_id=candidate_id)

    return {
        "candidate_id": candidate_id,
        "interviews": interviews
    }


@candidate_router.get("/candidates/by-pass-key/{pass_key}", response_model=CandidateResponse)
async def get_candidate_by_pass_key(
    pass_key: str,
    db: Session = Depends(get_db),
    candidate_service: CandidateService = Depends(get_candidate_service)
):
    """
    Get candidate by pass key (for interview access).
    This endpoint doesn't require authentication as it's used by candidates to access their interview.
    """
    try:
        candidate = candidate_service.get_candidate_by_pass_key(db=db, pass_key=pass_key)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid pass key"
            )
        return candidate
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve candidate: {str(e)}"
        )


@candidate_router.patch("/candidates/{candidate_id}/reset", response_model=CandidateResponse)
async def reset_candidate_interview(
    candidate_id: int,
    db: Session = Depends(get_db),
    candidate_service: CandidateService = Depends(get_candidate_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Reset candidate interview status and date.
    This removes the interview status and interview date, allowing the candidate to retake the interview.
    """
    try:
        candidate = candidate_service.reset_candidate_interview(db=db, candidate_id=candidate_id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        return candidate
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset candidate interview: {str(e)}"
        )


@candidate_router.get("/candidates/{candidate_id}/report", response_model=CandidateReportResponse)
async def get_candidate_report(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get the report for a specific candidate.
    """
    try:
        from app.crud.candidate_report import CandidateReportDAO
        report_dao = CandidateReportDAO()

        report = report_dao.get_by_candidate_id(db=db, candidate_id=candidate_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found for this candidate"
            )
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve candidate report: {str(e)}"
        )
