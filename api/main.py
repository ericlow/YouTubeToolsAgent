from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from api.models import Base
from api.routes.health_check import HealthCheck
from infrastructure.orm_database import engine

app = FastAPI(title="Youtube Research API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)

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


# HEALTH CHECK ENDPOINT
@app.get("/health")
def health():
    return HealthCheck.execute()



# =============================================================================
# WORKSPACE ENDPOINTS
# =============================================================================

# -----------------------------------------------------------------------------
# POST /api/v1/workspaces
# TRD Section 4.1
# -----------------------------------------------------------------------------
# Purpose: Create a new chat workspace
# Authentication: Required (X-API-Key header)
#
# Request:
#   - Empty body: {}
#
# Response (201 Created):
#   {
#     "workspace_id": "550e8400-e29b-41d4-a716-446655440000",  # UUID
#     "created_at": "2025-11-22T10:30:00Z"                     # ISO 8601
#   }
#
# Implementation notes:
#   - Generate new UUID for workspace
#   - Associate with authenticated user (future: from Cognito)
#   - Insert into workspaces table
#   - Return workspace_id and timestamp
#


PATH_WORKSPACES = "/api/v1/workspaces"
PATH_WORKSPACE = f"{PATH_WORKSPACES}/{{workspace_id}}"
PATH_VIDEOS = f"{PATH_WORKSPACE}/videos"
PATH_VIDEO = f"{PATH_VIDEOS}/{{video_id}}"
PATH_MESSAGES = f"{PATH_WORKSPACE}/messages"

# Workspaces
@app.post(PATH_WORKSPACES)
def create_workspace():
    return {
        "workspace_id": "",
        "created_at": ""
    }

@app.get(PATH_WORKSPACE)
def get_workspace(workspace_id:str):
    return {
        "workspace_id": "",
        "created_at": ""
    }

@app.get(PATH_WORKSPACES)
def get_workspaces():
    return {
        "workspace_id": "",
        "created_at": ""
    }

# videos
@app.get(PATH_VIDEOS)
def get_videos():
    return {
        "workspace_id": "",
        "created_at": ""
    }

@app.get(PATH_VIDEO)
def get_video():
    return {
        "workspace_id": "",
        "created_at": ""
    }

@app.post(PATH_VIDEOS)
def create_video():
    return {
        "workspace_id": "",
        "created_at": ""
    }

# messages
@app.get(PATH_MESSAGES)
def get_messages():
    return {
        "workspace_id": "",
        "created_at": ""
    }



# -----------------------------------------------------------------------------
# POST /api/v1/workspaces/{workspace_id}/videos
# TRD Section 4.1
# -----------------------------------------------------------------------------
# Purpose: Submit a YouTube URL to a workspace
# Authentication: Required (X-API-Key header)
#
# Path parameters:
#   - workspace_id: UUID of the workspace
#
# Request:
#   {
#     "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
#   }
#
# Response (200 OK):
#   {
#     "video_id": 123,                                          # Internal DB ID
#     "youtube_id": "dQw4w9WgXcQ",                             # YouTube video ID
#     "title": "Rick Astley - Never Gonna Give You Up",
#     "author": "Rick Astley",                                 # Channel name
#     "duration": 213,                                         # Seconds
#     "summary": "AI-generated summary of the video...",
#     "added_at": "2025-11-22T10:31:00Z"
#   }
#
# Behavior:
#   - Extract YouTube video ID from URL
#   - Check if video already exists in videos table (by youtube_id)
#   - If not exists:
#       * Fetch transcript using youtube-transcript-api
#       * Call Claude API to generate summary
#       * Store video metadata and transcript in videos table
#   - Associate video with workspace (workspace_videos table)
#   - Return video details with summary
#
# Error cases:
#   - 400: Invalid YouTube URL
#   - 400: Video has no available transcript
#   - 404: Workspace not found
#   - 500: Claude API error, YouTube API error
#
# TODO: Implement this endpoint


# -----------------------------------------------------------------------------
# GET /api/v1/workspaces/{workspace_id}/videos
# TRD Section 4.1
# -----------------------------------------------------------------------------
# Purpose: List all videos in a workspace
# Authentication: Required (X-API-Key header)
#
# Path parameters:
#   - workspace_id: UUID of the workspace
#
# Response (200 OK):
#   {
#     "videos": [
#       {
#         "video_id": 123,
#         "youtube_id": "dQw4w9WgXcQ",
#         "title": "Rick Astley - Never Gonna Give You Up",
#         "author": "Rick Astley",
#         "duration": 213,
#         "added_at": "2025-11-22T10:31:00Z"
#       },
#       ...
#     ]
#   }
#
# Implementation notes:
#   - Query workspace_videos join videos
#   - Filter by workspace_id
#   - Order by added_at DESC (most recent first)
#   - Return list of video metadata (no transcript or summary in list view)
#
# Error cases:
#   - 404: Workspace not found
#
# TODO: Implement this endpoint


# -----------------------------------------------------------------------------
# POST /api/v1/workspaces/{workspace_id}/chat
# TRD Section 4.1
# -----------------------------------------------------------------------------
# Purpose: Send a message and get AI response
# Authentication: Required (X-API-Key header)
#
# Path parameters:
#   - workspace_id: UUID of the workspace
#
# Request:
#   {
#     "message": "What is the main theme of this video?",
#     "video_id": 123  // optional: context for which video to focus on
#   }
#
# Response (200 OK):
#   {
#     "message_id": 456,
#     "role": "assistant",
#     "content": "The main theme is...",
#     "created_at": "2025-11-22T10:32:00Z"
#   }
#
# Behavior:
#   - Load workspace conversation history from messages table
#   - If video_id provided, load that video's transcript
#   - Build context for Claude API:
#       * System prompt with video transcripts from workspace
#       * Conversation history (all previous messages)
#       * New user message
#   - Call Claude API (synchronous for MVP)
#   - Save both user message and assistant response to messages table
#   - Return assistant response
#
# Implementation notes:
#   - Use claude-sonnet-4-5-20250929 model
#   - Include full conversation history for context
#   - Store both messages with workspace_id
#   - Link messages to video_id if provided (optional FK)
#
# Error cases:
#   - 400: Empty message
#   - 404: Workspace not found
#   - 404: video_id not found or not in workspace
#   - 500: Claude API error
#
# TODO: Implement this endpoint


# -----------------------------------------------------------------------------
# GET /api/v1/workspaces/{workspace_id}/messages
# TRD Section 4.1
# -----------------------------------------------------------------------------
# Purpose: Retrieve chat history for a workspace
# Authentication: Required (X-API-Key header)
#
# Path parameters:
#   - workspace_id: UUID of the workspace
#
# Query parameters:
#   - limit: Max messages to return (default: 50, max: 100)
#   - offset: Pagination offset (default: 0)
#
# Response (200 OK):
#   {
#     "messages": [
#       {
#         "message_id": 455,
#         "role": "user",
#         "content": "What is the main theme?",
#         "created_at": "2025-11-22T10:31:50Z"
#       },
#       {
#         "message_id": 456,
#         "role": "assistant",
#         "content": "The main theme is...",
#         "created_at": "2025-11-22T10:32:00Z"
#       }
#     ],
#     "total": 2,
#     "has_more": false
#   }
#
# Implementation notes:
#   - Query messages table filtered by workspace_id
#   - Order by created_at ASC (oldest first, chronological conversation)
#   - Apply pagination (limit, offset)
#   - Calculate total count and has_more flag
#
# Error cases:
#   - 404: Workspace not found
#
# TODO: Implement this endpoint

