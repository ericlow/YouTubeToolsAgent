from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from requests import Session


class CreateWorkspaceRequest(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceResponse(BaseModel):
    workspace_id: str
    name:str
    description: Optional[str]
    created_at: datetime

class WorkspaceListResponse(BaseModel):
    workspaces: list[WorkspaceResponse]

class WorkspaceService:
    @staticmethod
    def create(db: Session, request: CreateWorkspaceRequest):
        pass

    @staticmethod
    def list_all(db: Session):
        pass

    @staticmethod
    def get(db: Session, workspace_id):
        pass

    @staticmethod
    def delete(db: Session, workspace_id):
        pass
