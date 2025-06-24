"""
Question management router for REST API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db, get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.question import (
    QuestionResponse, QuestionCreate, QuestionUpdate, QuestionListResponse,
    QuestionFilter, BulkQuestionDelete, BulkQuestionCategoryUpdate,
    JobQuestionAssignment
)
from app.models.interview import QuestionCategory, QuestionImportance
from app.services.question_service import QuestionService
from app.crud.question import QuestionDAO
from app.crud.job import JobDAO
from app.crud.job_question import JobQuestionDAO

question_router = APIRouter()


def get_question_service() -> QuestionService:
    """Dependency to get QuestionService instance."""
    return QuestionService(
        question_dao=QuestionDAO(),
        job_dao=JobDAO(),
        job_question_dao=JobQuestionDAO()
    )


@question_router.get("/questions", response_model=QuestionListResponse)
async def get_questions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    category: Optional[QuestionCategory] = Query(None, description="Filter by category"),
    importance: Optional[QuestionImportance] = Query(None, description="Filter by importance"),
    search: Optional[str] = Query(None, description="Search term for title or question text"),
    created_by_user_id: Optional[int] = Query(None, description="Filter by creator user ID"),
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get questions with optional filtering and pagination.
    """
    # Build filters
    filters = QuestionFilter(
        category=category,
        importance=importance,
        search=search,
        created_by_user_id=created_by_user_id
    )
    
    return question_service.get_questions(db, page=page, page_size=page_size, filters=filters)


@question_router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get a specific question by ID.
    """
    question = question_service.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question


@question_router.post("/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_create: QuestionCreate,
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create a new question.
    """
    # Set the creator to the current user
    question_create.created_by_user_id = current_user.id
    
    try:
        return question_service.create_question(db, question_create)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create question: {str(e)}"
        )


@question_router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_update: QuestionUpdate,
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update an existing question.
    """
    question = question_service.update_question(db, question_id, question_update)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question


@question_router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete a question.
    """
    success = question_service.delete_question(db, question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )


@question_router.get("/questions/category/{category}", response_model=QuestionListResponse)
async def get_questions_by_category(
    category: QuestionCategory,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get questions filtered by category.
    """
    return question_service.get_questions_by_category(db, category, page=page, page_size=page_size)


@question_router.get("/questions/search/{search_term}", response_model=QuestionListResponse)
async def search_questions(
    search_term: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Search questions by title or question text.
    """
    return question_service.search_questions(db, search_term, page=page, page_size=page_size)


@question_router.post("/questions/bulk/delete")
async def bulk_delete_questions(
    bulk_delete: BulkQuestionDelete,
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete multiple questions.
    """
    try:
        deleted_count = question_service.bulk_delete_questions(db, bulk_delete)
        return {"message": f"Successfully deleted {deleted_count} questions"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete questions: {str(e)}"
        )


@question_router.post("/questions/bulk/update-category")
async def bulk_update_category(
    bulk_update: BulkQuestionCategoryUpdate,
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update category for multiple questions.
    """
    try:
        updated_count = question_service.bulk_update_category(db, bulk_update)
        return {"message": f"Successfully updated category for {updated_count} questions"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update question categories: {str(e)}"
        )


@question_router.post("/questions/assign-to-job")
async def assign_question_to_job(
    assignment: JobQuestionAssignment,
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Assign a question to a job.
    """
    try:
        success = question_service.assign_question_to_job(db, assignment)
        if success:
            return {"message": "Question successfully assigned to job"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign question to job"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to assign question to job: {str(e)}"
        )


@question_router.get("/questions/with-creator-info", response_model=QuestionListResponse)
async def get_questions_with_creator_info(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    question_service: QuestionService = Depends(get_question_service),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get questions with creator information.
    """
    return question_service.get_questions_with_creator_info(db, page=page, page_size=page_size)
