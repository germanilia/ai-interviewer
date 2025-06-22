from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse
from app.services.user_service import UserService
from app.dependencies import get_db, get_user_service

user_router = APIRouter()

@user_router.get("/users/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """
    Retrieve all users.
    """
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users

@user_router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """
    Retrieve a specific user by ID.
    """
    user = user_service.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user