from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.models import VideoModel, WorkspaceVideoModel
from components.services.youtube_service import YouTubeService
from infrastructure.orm_database import get_session

router = APIRouter()

# get all videos for a workspace
@router.get("/")
def get_videos(workspace_id:str, s:Session = Depends(get_session)):
    workspace_videos = s.query(WorkspaceVideoModel).filter_by(workspace_id=workspace_id).all()

    retval = { "videos": [] }
    retval["videos"].append(workspace_videos)
    return retval

# get a single video
@router.get("/")
def get_video():
    return { "val" : "not implemented"}

# add a video to a workspace
@router.post("/")
def create_video(workspace_id: str, url:str, s: Session = Depends(get_session)):
    # add a video to the workspace
    video_id = None
    created_at = None
    channel = None
    title = None

    try:
        youtube_service = YouTubeService()
        yt_video  = youtube_service.get_video(url)

        v = VideoModel(url, yt_video.transcript, yt_video.title, yt_video.author, "")
        s.add(v)

        s.commit()
        wvm = WorkspaceVideoModel(workspace_id, v.video_id)
        s.add(wvm)

        s.commit()
        video_id = v.video_id
        created_at = v.created_at
        channel = v.channel
        title = v.title
        workspace_video_creation_date = wvm.added_at
    except:
        print("Error when saving video")
    finally:
        return {
            "video_id": video_id,
            "url": url,
            "title": title,
            "channel": channel,
            "created_at": created_at,
            "workspace_id": workspace_id,
            "workspace_video_creation_date": workspace_video_creation_date
        }
