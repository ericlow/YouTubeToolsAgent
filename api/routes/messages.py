from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.models import MessageModel
from components.agents.chat_agent import ChatAgent
from components.anthropic.chat_message import ChatMessage
from components.anthropic.content import Content
from domain.models.agent_event import AgentEvent
from domain.repositories.message_repository import MessageRepository
from domain.services.workspace_service import WorkspaceService
from infrastructure.orm_database import get_session

router = APIRouter()

# Summary: HTTP routing, request/response

@router.get("/")
def get_messages(workspace_id: str, cursor: int= None, session: Session = Depends(get_session)):
    mr = MessageRepository(session)
    ws = WorkspaceService(mr)
    messages = ws.getMessages(workspace_id, cursor)
    return messages

@router.post("/")
def send_message(workspace_id:str, message: str, session: Session = Depends(get_session)):
    mr = MessageRepository(session)
    ws = WorkspaceService(mr)
    return ws.send_message(workspace_id, message)
