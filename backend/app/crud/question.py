"""
Question DAO for database operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.crud.base import BaseDAO
from app.models.interview import Question, QuestionCategory, QuestionImportance
from app.schemas.question import QuestionResponse, QuestionCreate, QuestionUpdate, QuestionWithCreator


class QuestionDAO(BaseDAO[Question, QuestionResponse, QuestionCreate, QuestionUpdate]):
    """Data Access Object for Question operations."""

    def __init__(self):
        super().__init__(Question, QuestionResponse)

    def get(self, db: Session, id: int) -> Optional[QuestionResponse]:
        """Get a question by ID."""
        question = db.query(self.model).filter(self.model.id == id).first()
        return QuestionResponse.from_model(question) if question else None

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[QuestionResponse]:
        """Get multiple questions with pagination."""
        questions = db.query(self.model).offset(skip).limit(limit).all()
        return [QuestionResponse.from_model(question) for question in questions]

    def create(self, db: Session, *, obj_in: QuestionCreate) -> QuestionResponse:
        """Create a new question."""
        question = obj_in.to_model()
        db.add(question)
        db.commit()
        db.refresh(question)
        return QuestionResponse.from_model(question)

    def update(self, db: Session, *, db_obj: Question, obj_in: QuestionUpdate) -> QuestionResponse:
        """Update an existing question."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return QuestionResponse.from_model(db_obj)

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete a question by ID."""
        question = db.query(self.model).filter(self.model.id == id).first()
        if question:
            db.delete(question)
            db.commit()
            return True
        return False

    def get_with_creator(self, db: Session, id: int) -> Optional[QuestionWithCreator]:
        """Get a question with creator details."""
        question = db.query(self.model).options(
            joinedload(self.model.created_by)
        ).filter(self.model.id == id).first()
        
        if question:
            return QuestionWithCreator.from_model(question)
        return None

    def get_by_category(self, db: Session, category: QuestionCategory, *, skip: int = 0, limit: int = 100) -> List[QuestionResponse]:
        """Get questions by category."""
        questions = db.query(self.model).filter(
            self.model.category == category
        ).offset(skip).limit(limit).all()
        return [QuestionResponse.from_model(question) for question in questions]

    def get_by_importance(self, db: Session, importance: QuestionImportance, *, skip: int = 0, limit: int = 100) -> List[QuestionResponse]:
        """Get questions by importance level."""
        questions = db.query(self.model).filter(
            self.model.importance == importance
        ).offset(skip).limit(limit).all()
        return [QuestionResponse.from_model(question) for question in questions]

    def get_by_creator(self, db: Session, creator_id: int, *, skip: int = 0, limit: int = 100) -> List[QuestionResponse]:
        """Get questions created by a specific user."""
        questions = db.query(self.model).filter(
            self.model.created_by_user_id == creator_id
        ).offset(skip).limit(limit).all()
        return [QuestionResponse.from_model(question) for question in questions]

    def search_by_text(self, db: Session, search_text: str, *, skip: int = 0, limit: int = 100) -> List[QuestionResponse]:
        """Search questions by title or question text."""
        questions = db.query(self.model).filter(
            (self.model.title.ilike(f"%{search_text}%")) |
            (self.model.question_text.ilike(f"%{search_text}%"))
        ).offset(skip).limit(limit).all()
        return [QuestionResponse.from_model(question) for question in questions]

    def get_by_filters(self, db: Session, *, category: Optional[QuestionCategory] = None, 
                      importance: Optional[QuestionImportance] = None, 
                      creator_id: Optional[int] = None,
                      skip: int = 0, limit: int = 100) -> List[QuestionResponse]:
        """Get questions with multiple filters."""
        query = db.query(self.model)
        
        if category:
            query = query.filter(self.model.category == category)
        if importance:
            query = query.filter(self.model.importance == importance)
        if creator_id:
            query = query.filter(self.model.created_by_user_id == creator_id)
            
        questions = query.offset(skip).limit(limit).all()
        return [QuestionResponse.from_model(question) for question in questions]
