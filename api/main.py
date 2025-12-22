from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.exc import OperationalError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from api.models import Base
from infrastructure.orm_database import engine
from api.routes import workspaces, health, videos, messages, users
from logger_config import setup_logging, getLogger

setup_logging()
logger = getLogger(__name__)

app = FastAPI(title="Youtube Research API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Handles startup and shutdown events.
    """

    try:
        # Startup: Create database tables
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        logger.error("\n❌ ERROR: Cannot connect to database")
        logger.error("\nMake sure PostgreSQL is running")
        logger.error(e)
        raise SystemExit(1)  # Exit cleanly instead of showing stack trace
    yield

    # Shutdown: Clean up resources if needed
    # e.g., close database connections, etc.

app = FastAPI(
    title="YouTube Research Tool",
    description="AI-powered research tool for YouTube video content",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An unexpected error occurred"
        }
    )

@app.get("/")
def root():
    return { "message" : "app is running"}

PATH_HEALTH = "/api/v1/health"
PATH_USERS  = "/api/v1/users"
PATH_WORKSPACES = "/api/v1/workspaces"
PATH_WORKSPACE = f"{PATH_WORKSPACES}/{{workspace_id}}"
PATH_VIDEOS = f"{PATH_WORKSPACE}/videos"
PATH_MESSAGES = f"{PATH_WORKSPACE}/messages"

app.include_router(users.router, prefix=PATH_USERS)
app.include_router(workspaces.router, prefix=PATH_WORKSPACES)
app.include_router(videos.router, prefix=PATH_VIDEOS)
app.include_router(health.router, prefix=PATH_HEALTH)
app.include_router(messages.router, prefix=PATH_MESSAGES)
