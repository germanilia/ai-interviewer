from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import router as api_router
from app.core.config_service import settings
from app.db.init_db import init_db
from app.core.logging_service import get_logger
from app.middlewaremiddleware.logging_middleware import RequestLoggingMiddleware

# Configure logging
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup logic
    logger.info("Starting application database setup")
    success = init_db()
    if success:
        logger.info("Database setup completed successfully", service="database", status="initialized")
    else:
        logger.error("Database setup failed", service="database", status="failed")
        raise RuntimeError("Failed to initialize database")

    yield

    # Shutdown logic
    logger.info("Application shutting down")

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A FastAPI backend for apartment management and customer service chatbot",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Support Team",
        "url": "http://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

# 1. Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# 2. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # This is now a property that returns a list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    from app.core.config_service import config_service

    # Get host and port from configuration
    host = config_service.get("host", "0.0.0.0")
    port = config_service.get("port", 9000)

    logger.info(
        "Starting application server",
        host=host,
        port=port,
        environment=config_service._env
    )
    
    uvicorn.run(app, host=host, port=port)