"""
Job management router for REST API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db, get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.job import (
    JobResponse, JobCreate, JobCreateRequest, JobUpdate, JobListResponse, JobFilter,
    JobStatistics, JobCloneRequest, JobWithQuestions
)
from app.services.job_service import JobService
from app.crud.job import JobDAO
from app.crud.job_question import JobQuestionDAO

job_router = APIRouter()


def get_job_service() -> JobService:
    """Dependency to get JobService instance."""
    return JobService(
        job_dao=JobDAO(),
        job_question_dao=JobQuestionDAO()
    )


@job_router.get("/jobs", response_model=JobListResponse)
async def get_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    search: Optional[str] = Query(None, description="Search term for job title"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get jobs with pagination, search, and filtering.
    """
    try:
        filters = JobFilter(
            search=search,
            department=department,
            created_by_user_id=None  # Allow all users to see all jobs
        )
        
        return job_service.get_jobs(
            db=db,
            page=page,
            page_size=page_size,
            filters=filters
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve jobs: {str(e)}"
        )


@job_router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreateRequest,
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create a new job position.
    """
    try:
        # Create a new JobCreate object with the current user ID
        job_create_data = JobCreate(
            title=job_data.title,
            description=job_data.description,
            department=job_data.department,
            created_by_user_id=current_user.id
        )

        return job_service.create_job(db=db, job_create=job_create_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create job: {str(e)}"
        )


@job_router.get("/jobs/departments", response_model=list[str])
async def get_departments(
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get list of unique departments.
    """
    return job_service.get_departments(db=db)


@job_router.get("/jobs/search", response_model=JobListResponse)
async def search_jobs(
    q: str = Query(..., description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Search jobs by title.
    """
    return job_service.search_jobs(
        db=db,
        search_term=q,
        page=page,
        page_size=page_size
    )


@job_router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get a specific job by ID.
    """
    job = job_service.get_job(db=db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job


@job_router.put("/jobs/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update an existing job.
    """
    updated_job = job_service.update_job(db=db, job_id=job_id, job_update=job_update)
    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return updated_job


@job_router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete a job.
    """
    success = job_service.delete_job(db=db, job_id=job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )


@job_router.get("/jobs/{job_id}/template", response_model=JobWithQuestions)
async def get_job_template(
    job_id: int,
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get a job's question template.
    """
    job_with_questions = job_service.get_job_with_questions(db=db, job_id=job_id)
    if not job_with_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job_with_questions


@job_router.post("/jobs/{job_id}/clone")
async def clone_job_template(
    job_id: int,
    clone_request: JobCloneRequest,
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Clone question template from one job to another.
    """
    try:
        # Override source job ID from URL parameter
        clone_request.source_job_id = job_id
        
        success = job_service.clone_job_template(db=db, clone_request=clone_request)
        if success:
            return {"message": "Template cloned successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to clone template"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@job_router.get("/jobs/{job_id}/statistics", response_model=JobStatistics)
async def get_job_statistics(
    job_id: int,
    db: Session = Depends(get_db),
    job_service: JobService = Depends(get_job_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get statistics for a specific job.
    """
    statistics = job_service.get_job_statistics(db=db, job_id=job_id)
    if not statistics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return statistics
