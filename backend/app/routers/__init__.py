# backend/app/routers/__init__.py

from fastapi import APIRouter
from .user import user_router
from .auth import auth_router
from .dev import dev_router
from .candidate import candidate_router
from app.core.config_service import config_service

router = APIRouter()

# Health check endpoint
@router.get("/api/v1/health")
async def health_check():
    """Health check endpoint for monitoring and testing"""
    import os

    # Debug print to see what environment is loaded
    env_info = {
        "APP_ENV": os.getenv("APP_ENV"),
        "USE_MOCK_COGNITO": os.getenv("USE_MOCK_COGNITO"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "config_service_env": config_service._env,
        "config_service_testing": config_service.is_testing(),
        "config_service_mock_cognito": config_service.use_mock_cognito(),
        "database_url": config_service.get_database_url()
    }
    print(f"[HEALTH DEBUG] Environment info: {env_info}")

    return {
        "status": "healthy",
        "service": "backend",
        "environment": config_service._env,
        "use_mock_cognito": config_service.use_mock_cognito(),
        "is_testing": config_service.is_testing(),
        "database_type": "sqlite" if config_service.get_database_url().startswith("sqlite") else "postgresql"
    }

# Include route definitions
router.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
router.include_router(user_router, prefix="/api/v1", tags=["users"])
router.include_router(candidate_router, prefix="/api/v1", tags=["candidates"])
router.include_router(dev_router, prefix="/api/v1/dev", tags=["development"])