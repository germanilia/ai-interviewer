"""
Base DAO classes for database operations.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Type variables for generic DAO
ModelType = TypeVar("ModelType")  # SQLAlchemy model
SchemaType = TypeVar("SchemaType", bound=BaseModel)  # Pydantic schema
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType, SchemaType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Abstract base class for Data Access Objects.
    Provides common CRUD operations that return Pydantic objects.
    """

    def __init__(self, model: Type[ModelType], schema: Type[SchemaType]):
        """
        Initialize DAO with model and schema types.
        
        Args:
            model: SQLAlchemy model class
            schema: Pydantic schema class for responses
        """
        self.model = model
        self.schema = schema

    def _to_schema(self, db_obj: ModelType) -> SchemaType:
        """Convert SQLAlchemy model to Pydantic schema."""
        return self.schema.model_validate(db_obj)

    def _to_schema_list(self, db_objs: List[ModelType]) -> List[SchemaType]:
        """Convert list of SQLAlchemy models to list of Pydantic schemas."""
        return [self._to_schema(obj) for obj in db_objs]

    @abstractmethod
    def get(self, db: Session, id: int) -> Optional[SchemaType]:
        """Get a single record by ID."""
        pass

    @abstractmethod
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[SchemaType]:
        """Get multiple records with pagination."""
        pass

    @abstractmethod
    def create(self, db: Session, *, obj_in: CreateSchemaType, created_by_user_id: int | None = None) -> SchemaType:
        """Create a new record."""
        pass

    @abstractmethod
    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> SchemaType:
        """Update an existing record."""
        pass

    @abstractmethod
    def delete(self, db: Session, *, id: int) -> bool:
        """Delete a record by ID."""
        pass
