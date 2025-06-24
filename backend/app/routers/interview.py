"""
Interview router for FastAPI endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.interview import (
    InterviewResponse, 
    InterviewCreate, 
    InterviewUpdate, 
    InterviewListResponse
)
from app.models.interview import InterviewStatus
from app.services.interview_service import InterviewService
from app.crud.interview import InterviewDAO
from app.crud.candidate import CandidateDAO
from app.crud.job import JobDAO

interview_router = APIRouter()


def get_interview_service() -> InterviewService:
    """Dependency to get InterviewService instance."""
    return InterviewService(
        interview_dao=InterviewDAO(),
        candidate_dao=CandidateDAO(),
        job_dao=JobDAO()
    )


@interview_router.get("/interviews", response_model=InterviewListResponse)
async def get_interviews(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search term for candidate name"),
    candidate_id: Optional[int] = Query(None, description="Filter by candidate ID"),
    job_id: Optional[int] = Query(None, description="Filter by job ID"),
    db: Session = Depends(get_db),
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get interviews with pagination, search, and filtering.
    """
    try:
        return interview_service.get_interviews(
            db=db,
            page=page,
            page_size=page_size,
            status=status_filter,
            search=search,
            candidate_id=candidate_id,
            job_id=job_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interviews: {str(e)}"
        )


@interview_router.get("/interviews/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get a specific interview by ID.
    """
    interview = interview_service.get_interview_by_id(db=db, interview_id=interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    return interview


@interview_router.post("/interviews", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_create: InterviewCreate,
    db: Session = Depends(get_db),
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create a new interview.
    """
    try:
        return interview_service.create_interview(db=db, interview_create=interview_create, created_by_user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview: {str(e)}"
        )


@interview_router.put("/interviews/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: int,
    interview_update: InterviewUpdate,
    db: Session = Depends(get_db),
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update an interview.
    """
    try:
        updated_interview = interview_service.update_interview(
            db=db,
            interview_id=interview_id,
            interview_update=interview_update
        )
        if not updated_interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        return updated_interview
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update interview: {str(e)}"
        )


@interview_router.patch("/interviews/{interview_id}/status")
async def change_interview_status(
    interview_id: int,
    new_status: InterviewStatus,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Change interview status.
    """
    try:
        updated_interview = interview_service.change_interview_status(
            db=db,
            interview_id=interview_id,
            new_status=new_status,
            reason=reason
        )
        if not updated_interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        return updated_interview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change interview status: {str(e)}"
        )


@interview_router.patch("/interviews/{interview_id}/cancel")
async def cancel_interview(
    interview_id: int,
    reason: str = Body(..., description="Cancellation reason"),
    db: Session = Depends(get_db),
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Cancel an interview.
    """
    try:
        updated_interview = interview_service.cancel_interview(
            db=db,
            interview_id=interview_id,
            reason=reason
        )
        if not updated_interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        return updated_interview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel interview: {str(e)}"
        )


@interview_router.delete("/interviews/{interview_id}")
async def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete an interview.
    """
    try:
        deleted = interview_service.delete_interview(db=db, interview_id=interview_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview not found"
            )
        return {"message": "Interview deleted successfully"}
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete interview: {str(e)}"
        )








@interview_router.post("/interviews/bulk/cancel")
async def bulk_cancel_interviews(
    interview_ids: List[int] = Body(..., description="List of interview IDs to cancel"),
    reason: str = Body(..., description="Cancellation reason"),
    db: Session = Depends(get_db),
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Cancel multiple interviews in bulk.
    """
    try:
        results = []
        for interview_id in interview_ids:
            try:
                updated_interview = interview_service.cancel_interview(
                    db=db,
                    interview_id=interview_id,
                    reason=reason
                )
                if updated_interview:
                    results.append({"interview_id": interview_id, "status": "cancelled"})
                else:
                    results.append({"interview_id": interview_id, "status": "not_found"})
            except Exception as e:
                results.append({"interview_id": interview_id, "status": "error", "error": str(e)})

        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel interviews: {str(e)}"
        )


@interview_router.post("/interviews/bulk/delete")
async def bulk_delete_interviews(
    interview_ids: List[int] = Body(..., description="List of interview IDs to delete"),
    db: Session = Depends(get_db),
    interview_service: InterviewService = Depends(get_interview_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete multiple interviews in bulk.
    """
    try:
        results = []
        for interview_id in interview_ids:
            try:
                deleted = interview_service.delete_interview(db=db, interview_id=interview_id)
                if deleted:
                    results.append({"interview_id": interview_id, "status": "deleted"})
                else:
                    results.append({"interview_id": interview_id, "status": "not_found"})
            except Exception as e:
                results.append({"interview_id": interview_id, "status": "error", "error": str(e)})

        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete interviews: {str(e)}"
        )
