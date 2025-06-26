"""
Custom prompt router for CRUD operations on custom prompts.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional, List
from sqlalchemy.orm import Session
from app.schemas.custom_prompt import (
    CustomPromptResponse, CustomPromptCreate, CustomPromptUpdate, 
    CustomPromptListResponse
)
from app.models.custom_prompt import PromptType
from app.crud.custom_prompt import custom_prompt_dao
from app.dependencies import get_db, get_current_active_user
from app.schemas.user import UserResponse
import logging

logger = logging.getLogger(__name__)

custom_prompt_router = APIRouter()


@custom_prompt_router.get("/custom-prompts", response_model=CustomPromptListResponse)
async def get_custom_prompts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    prompt_type: Optional[PromptType] = Query(None, description="Filter by prompt type"),
    active_only: bool = Query(True, description="Return only active prompts"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get list of custom prompts with optional filtering.
    """
    try:
        if prompt_type:
            prompts = custom_prompt_dao.get_by_type(
                db=db, 
                prompt_type=prompt_type, 
                active_only=active_only
            )
            # Apply pagination manually for filtered results
            total = len(prompts)
            prompts = prompts[skip:skip + limit]
        else:
            if active_only:
                # Get all prompts and filter active ones
                all_prompts = custom_prompt_dao.get_multi(db=db, skip=0, limit=10000)
                prompts = [p for p in all_prompts if p.is_active]
                total = len(prompts)
                prompts = prompts[skip:skip + limit]
            else:
                prompts = custom_prompt_dao.get_multi(db=db, skip=skip, limit=limit)
                # For total count, we'd need a separate count query
                total = len(custom_prompt_dao.get_multi(db=db, skip=0, limit=10000))

        return CustomPromptListResponse(
            prompts=prompts,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.exception(f"Failed to get custom prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve custom prompts: {str(e)}"
        )


@custom_prompt_router.post("/custom-prompts", response_model=CustomPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_prompt(
    prompt_data: CustomPromptCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create a new custom prompt. If a prompt of the same type already exists, it will be replaced.
    """
    try:
        # Set the created_by_user_id from the current user
        prompt_data.created_by_user_id = current_user.id

        # Check if a prompt of this type already exists
        existing_prompt = custom_prompt_dao.get_active_by_type(db=db, prompt_type=prompt_data.prompt_type)

        if existing_prompt:
            # Replace the existing prompt by updating it
            db_prompt = db.query(custom_prompt_dao.model).filter(
                custom_prompt_dao.model.id == existing_prompt.id
            ).first()

            if db_prompt:
                # Update the existing prompt with new data
                update_data = CustomPromptUpdate(
                    name=prompt_data.name,
                    content=prompt_data.content,
                    description=prompt_data.description,
                    is_active=True
                )
                return custom_prompt_dao.update(db=db, db_obj=db_prompt, obj_in=update_data)

        # Create new prompt if none exists
        return custom_prompt_dao.create(
            db=db,
            obj_in=prompt_data,
            created_by_user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Failed to create custom prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom prompt: {str(e)}"
        )


@custom_prompt_router.get("/custom-prompts/{prompt_id}", response_model=CustomPromptResponse)
async def get_custom_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get a specific custom prompt by ID.
    """
    prompt = custom_prompt_dao.get(db=db, id=prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom prompt not found"
        )
    return prompt


@custom_prompt_router.put("/custom-prompts/{prompt_id}", response_model=CustomPromptResponse)
async def update_custom_prompt(
    prompt_id: int,
    prompt_data: CustomPromptUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update an existing custom prompt.
    """
    # Get the existing prompt
    db_prompt = db.query(custom_prompt_dao.model).filter(custom_prompt_dao.model.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom prompt not found"
        )
    
    try:
        return custom_prompt_dao.update(db=db, db_obj=db_prompt, obj_in=prompt_data)
    except Exception as e:
        logger.exception(f"Failed to update custom prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update custom prompt: {str(e)}"
        )


@custom_prompt_router.delete("/custom-prompts/{prompt_id}")
async def delete_custom_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete a custom prompt.
    """
    success = custom_prompt_dao.delete(db=db, id=prompt_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom prompt not found"
        )
    return {"message": "Custom prompt deleted successfully"}


@custom_prompt_router.post("/custom-prompts/{prompt_id}/activate", response_model=CustomPromptResponse)
async def activate_custom_prompt(
    prompt_id: int,
    deactivate_others: bool = Query(True, description="Deactivate other prompts of the same type"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Activate a custom prompt and optionally deactivate others of the same type.
    """
    try:
        prompt = custom_prompt_dao.activate_prompt(
            db=db, 
            id=prompt_id, 
            deactivate_others=deactivate_others
        )
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Custom prompt not found"
            )
        return prompt
    except Exception as e:
        logger.exception(f"Failed to activate custom prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate custom prompt: {str(e)}"
        )


@custom_prompt_router.get("/custom-prompts/types/{prompt_type}/active", response_model=Optional[CustomPromptResponse])
async def get_active_prompt_by_type(
    prompt_type: PromptType,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get the active custom prompt for a specific type.
    """
    try:
        prompt = custom_prompt_dao.get_active_by_type(db=db, prompt_type=prompt_type)
        return prompt
    except Exception as e:
        logger.exception(f"Failed to get active prompt by type: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active prompt: {str(e)}"
        )


@custom_prompt_router.get("/custom-prompts/stats/count-by-type")
async def get_prompt_count_by_type(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get count of prompts by type for dashboard statistics.
    """
    try:
        counts = custom_prompt_dao.get_count_by_type(db=db)
        return {"counts": counts}
    except Exception as e:
        logger.exception(f"Failed to get prompt counts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prompt counts: {str(e)}"
        )
