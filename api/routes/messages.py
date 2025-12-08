from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.models import MessageModel
from components.agents.chat_agent import ChatAgent
from infrastructure.orm_database import get_session

router = APIRouter()

# send a message
# messages
@router.get("/")
def get_messages(workspace_id: str, cursor: int= None, s: Session = Depends(get_session)):
    messages = s.query(MessageModel).filter_by(workspace_id=workspace_id).order_by(MessageModel.created_at.asc()).all()
    return messages

@router.post("/")
def create_message(workspace_id:str, message: str, s: Session = Depends(get_session)):
    message = MessageModel(workspace_id, MessageModel.ROLE_USER, message)
    s.add(message)
    s.commit()

    agent = ChatAgent()
    print(agent.is_healthy())
    agent_message = agent.chat(message.content)
    message = MessageModel(workspace_id, MessageModel.ROLE_ASSISTANT, agent_message)
    s.add(message)
    s.commit()
    return message
