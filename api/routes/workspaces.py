from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.models import WorkspaceModel
from infrastructure.orm_database import get_session

router = APIRouter()

# Workspaces
@router.post("/")
def create_workspace(user_id:int, name:str = None, workspace_id:str = None, s:Session = Depends(get_session)):
    retval = {
        "workspace_id": "",
        "name": name,
        "user_id": user_id,
        "created_at": ""
    }
    if workspace_id:
        # check for existing
        # retreive record
        # update name
        # save
        if name is not None:
            workspace = s.query(WorkspaceModel).filter_by(workspace_id=workspace_id).one_or_none()
            workspace.name = name
            s.add(workspace)
            s.commit()
            retval["workspace_id"] = workspace.workspace_id
    else:
        workspace = WorkspaceModel(user_id=user_id, name = name)
        s.add(workspace)
        s.commit()
        retval["workspace_id"] = workspace.workspace_id
        retval["created_at"] = workspace.created_at
    return retval

@router.get("/{workspace_id}")
def get_workspace(workspace_id:str, s:Session = Depends(get_session)):
    workspace = s.query(WorkspaceModel).filter_by(workspace_id=workspace_id).one_or_none()
    retval = workspace
    return retval

@router.get("/")
def get_workspaces(s:Session = Depends(get_session)):

    workspaces = s.query(WorkspaceModel).order_by(WorkspaceModel.created_at.desc()).all()
    retval = { "workspaces": [] }

    retval["workspaces"].append(workspaces)
    return retval
