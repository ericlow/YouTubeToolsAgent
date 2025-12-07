from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models import WorkspaceModel
from domain.services.workspace_service import WorkspaceService
from infrastructure.orm_database import get_session

router = APIRouter()

# Workspaces
@router.post("/")
def create_workspace():
    return {
        "workspace_id": "",
        "created_at": ""
    }

@router.get("/{workspace_id}")
def get_workspace(workspace_id:str, s:Session = Depends(get_session)):
    workspaces = s.query(WorkspaceModel).order_by(WorkspaceModel.created_at.desc()).all()
    retval = { "workspaces": [] }

    retval["workspaces"].append(workspaces)
    return retval

@router.get("/")
def get_workspaces(s:Session = Depends(get_session)):

    workspaces = s.query(WorkspaceModel).order_by(WorkspaceModel.created_at.desc()).all()
    retval = { "workspaces": [] }

    retval["workspaces"].append(workspaces)
    return retval
