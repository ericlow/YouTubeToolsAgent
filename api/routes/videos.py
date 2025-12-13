from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.models import VideoModel, WorkspaceVideoModel
from components.services.youtube_service import YouTubeService
from domain.repositories.video_repository import VideoRepository
from infrastructure.orm_database import get_session

router = APIRouter()

# get all videos for a workspace
@router.get("/")
def get_videos(workspace_id:str, s:Session = Depends(get_session)):

    retval = { "videos": [] }
    # retval["videos"].append(workspace_videos)

    video_repository = VideoRepository(s)
    video_repository.get_videos(workspace_id)
    return retval

# get a single video
@router.get("/{video_id}")
def get_video(workspace_id:str, video_id:int):
    return { "val" : "not implemented"}
