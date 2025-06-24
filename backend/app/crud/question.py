"""
Question DAO for database operations.
"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.crud.base import BaseDAO
from app.models.interview import Question, QuestionCategory, QuestionImportance
from app.schemas.question import QuestionResponse, QuestionCreate, QuestionUpdate, QuestionFilter


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

    def get_multi_with_filter(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[QuestionFilter] = None
    ) -> Tuple[List[QuestionResponse], int]:
        """Get multiple questions with filtering and return total count."""
        query = db.query(self.model).options(joinedload(Question.created_by))

        # Apply filters
        if filters:
            if filters.category:
                query = query.filter(self.model.category == filters.category)

            if filters.importance:
                query = query.filter(self.model.importance == filters.importance)

            if filters.created_by_user_id:
                query = query.filter(self.model.created_by_user_id == filters.created_by_user_id)

            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        self.model.title.ilike(search_term),
                        self.model.question_text.ilike(search_term)
                    )
                )

        # Get total count before pagination
        total = query.count()

        # Apply pagination and get results
        questions = query.offset(skip).limit(limit).all()

        return [QuestionResponse.from_model(question) for question in questions], total

    def get_questions_by_category(self, db: Session, category: QuestionCategory, *, skip: int = 0, limit: int = 100) -> List[QuestionResponse]:
        """Get questions by category."""
        questions = db.query(self.model).filter(
            self.model.category == category
        ).offset(skip).limit(limit).all()
        return [QuestionResponse.from_model(question) for question in questions]

    def search_questions(self, db: Session, search_term: str, *, skip: int = 0, limit: int = 100) -> List[QuestionResponse]:
        """Search questions by title or question text."""
        search_pattern = f"%{search_term}%"
        questions = db.query(self.model).filter(
            or_(
                self.model.title.ilike(search_pattern),
                self.model.question_text.ilike(search_pattern)
            )
        ).offset(skip).limit(limit).all()
        return [QuestionResponse.from_model(question) for question in questions]

    def get_by_ids(self, db: Session, question_ids: List[int]) -> List[QuestionResponse]:
        """Get multiple questions by their IDs."""
        questions = db.query(self.model).filter(self.model.id.in_(question_ids)).all()
        return [QuestionResponse.from_model(question) for question in questions]

    def delete_multiple(self, db: Session, question_ids: List[int]) -> int:
        """Delete multiple questions by their IDs. Returns count of deleted questions."""
        deleted_count = db.query(self.model).filter(self.model.id.in_(question_ids)).delete(synchronize_session=False)
        db.commit()
        return deleted_count

    def update_category_bulk(self, db: Session, question_ids: List[int], new_category: QuestionCategory) -> int:
        """Update category for multiple questions. Returns count of updated questions."""
        updated_count = db.query(self.model).filter(self.model.id.in_(question_ids)).update(
            {self.model.category: new_category},
            synchronize_session=False
        )
        db.commit()
        return updated_count

    def get_questions_with_creator_info(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[QuestionResponse]:
        """Get questions with creator information."""
        questions = db.query(self.model).options(
            joinedload(Question.created_by)
        ).offset(skip).limit(limit).all()

        question_responses = []
        for question in questions:
            response = QuestionResponse.from_model(question)
            if question.created_by:
                response.created_by_name = f"{question.created_by.first_name} {question.created_by.last_name}".strip()
            question_responses.append(response)

        return question_responses

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
