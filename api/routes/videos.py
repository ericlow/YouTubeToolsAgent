from fastapi import APIRouter

router = APIRouter()

# videos
@router.get("/")
def get_videos():
    return {
        "workspace_id": "",
        "created_at": ""
    }

@router.get("/")
def get_video():
    return {
        "workspace_id": "",
        "created_at": ""
    }

@router.post("/")
def create_video():
    return {
        "workspace_id": "",
        "created_at": ""
    }
