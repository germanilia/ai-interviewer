"""
Data Access Object for Custom Prompt operations.
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import BaseDAO
from app.models.custom_prompt import CustomPrompt, PromptType
from app.schemas.custom_prompt import (
    CustomPromptResponse, CustomPromptCreate, CustomPromptUpdate
)

logger = logging.getLogger(__name__)


class CustomPromptDAO(BaseDAO[CustomPrompt, CustomPromptResponse, CustomPromptCreate, CustomPromptUpdate]):
    """Data Access Object for CustomPrompt operations."""

    def __init__(self):
        super().__init__(CustomPrompt, CustomPromptResponse)

    def get(self, db: Session, id: int) -> Optional[CustomPromptResponse]:
        """Get a custom prompt by ID."""
        prompt = db.query(self.model).filter(self.model.id == id).first()
        return CustomPromptResponse.from_model(prompt) if prompt else None

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[CustomPromptResponse]:
        """Get multiple custom prompts with pagination."""
        prompts = db.query(self.model).offset(skip).limit(limit).all()
        return [CustomPromptResponse.from_model(prompt) for prompt in prompts]

    def create(self, db: Session, *, obj_in: CustomPromptCreate, created_by_user_id: int | None = None) -> CustomPromptResponse:
        """Create a new custom prompt."""
        # Use the created_by_user_id from the schema if provided, otherwise use the parameter
        user_id = obj_in.created_by_user_id if hasattr(obj_in, 'created_by_user_id') else created_by_user_id
        if user_id is None:
            raise ValueError("created_by_user_id is required")

        db_obj = self.model(
            prompt_type=obj_in.prompt_type,
            name=obj_in.name,
            content=obj_in.content,
            description=obj_in.description,
            is_active=obj_in.is_active,
            created_by_user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Created custom prompt: {db_obj.name} (ID: {db_obj.id})")
        return CustomPromptResponse.from_model(db_obj)

    def update(self, db: Session, *, db_obj: CustomPrompt, obj_in: CustomPromptUpdate) -> CustomPromptResponse:
        """Update an existing custom prompt."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Updated custom prompt: {db_obj.name} (ID: {db_obj.id})")
        return CustomPromptResponse.from_model(db_obj)

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete a custom prompt by ID."""
        prompt = db.query(self.model).filter(self.model.id == id).first()
        if prompt:
            db.delete(prompt)
            db.commit()
            logger.info(f"Deleted custom prompt: {prompt.name} (ID: {id})")
            return True
        return False

    def get_by_type(self, db: Session, prompt_type: PromptType, *, active_only: bool = True) -> List[CustomPromptResponse]:
        """Get custom prompts by type."""
        query = db.query(self.model).filter(self.model.prompt_type == prompt_type)
        if active_only:
            query = query.filter(self.model.is_active == True)
        
        prompts = query.all()
        return [CustomPromptResponse.from_model(prompt) for prompt in prompts]

    def get_active_by_type(self, db: Session, prompt_type: PromptType) -> Optional[CustomPromptResponse]:
        """Get the first active custom prompt by type."""
        prompt = (
            db.query(self.model)
            .filter(self.model.prompt_type == prompt_type)
            .filter(self.model.is_active == True)
            .first()
        )
        return CustomPromptResponse.from_model(prompt) if prompt else None

    def deactivate_all_by_type(self, db: Session, prompt_type: PromptType) -> int:
        """Deactivate all prompts of a specific type. Returns count of deactivated prompts."""
        count = (
            db.query(self.model)
            .filter(self.model.prompt_type == prompt_type)
            .filter(self.model.is_active == True)
            .update({"is_active": False})
        )
        db.commit()
        logger.info(f"Deactivated {count} prompts of type {prompt_type}")
        return count

    def activate_prompt(self, db: Session, id: int, *, deactivate_others: bool = True) -> Optional[CustomPromptResponse]:
        """
        Activate a specific prompt and optionally deactivate others of the same type.
        
        Args:
            db: Database session
            id: ID of the prompt to activate
            deactivate_others: Whether to deactivate other prompts of the same type
        
        Returns:
            The activated prompt or None if not found
        """
        prompt = db.query(self.model).filter(self.model.id == id).first()
        if not prompt:
            return None

        if deactivate_others:
            # Deactivate all other prompts of the same type
            db.query(self.model).filter(
                self.model.prompt_type == prompt.prompt_type,
                self.model.id != id
            ).update({"is_active": False})

        # Activate the target prompt
        prompt.is_active = True
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        logger.info(f"Activated custom prompt: {prompt.name} (ID: {id})")
        return CustomPromptResponse.from_model(prompt)

    def get_count_by_type(self, db: Session) -> dict[PromptType, int]:
        """Get count of prompts by type."""
        from sqlalchemy import func
        
        result = (
            db.query(self.model.prompt_type, func.count(self.model.id))
            .group_by(self.model.prompt_type)
            .all()
        )
        
        return {prompt_type: count for prompt_type, count in result}


# Create instance for dependency injection
custom_prompt_dao = CustomPromptDAO()
