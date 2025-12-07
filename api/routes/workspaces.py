from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
from domain.services.workspace_service import WorkspaceService

router = APIRouter()

@router.post
def create_workspace(
        request: CreateWorkspaceRequest,
        db:Session = Depends(get_db)
):
    return WorkspaceService.create(db, request)