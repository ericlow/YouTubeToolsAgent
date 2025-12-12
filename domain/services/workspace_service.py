from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from api.models import MessageModel
from api.routes.messages import MessageRepository
from components.anthropic.chat_message import ChatMessage
from components.anthropic.role import Role
from api.models import MessageModel
from components.agents.chat_agent import ChatAgent
from components.anthropic.chat_message import ChatMessage
from components.anthropic.content import Content
from domain.models.agent_event import AgentEvent
from domain.repositories.message_repository import MessageRepository
from infrastructure.orm_database import get_session



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
    def __init__(self, message_repository:MessageRepository):
        self.message_repository = message_repository

    def getMessages(self, workspace_id, cursor):
        return self.message_repository.get_messages(workspace_id)

    def send_message(self, workspace_id, message:str):
        def handle_event(event: AgentEvent):
            print(f"Message\nType:{event.type} \nMessage: {event.data}")
            if event.type is not 'end_turn':
                self.message_repository.create_message(workspace_id,
                                                   MessageModel.ROLE_ASSISTANT,
                                                   event.data)

        self.message_repository.create_message(workspace_id, MessageModel.ROLE_USER, message)
        messages = self.message_repository.get_messages(workspace_id)


        agent_messages = [ChatMessage(Role(message.role), message.content) for message in messages]
        agent_context: list[Content] = []

        # Ask Agent to take next step
        agent = ChatAgent(agent_context, agent_messages)
        agent_message = agent.chat(message, handle_event)

        self.message_repository.create_message(workspace_id, MessageModel.ROLE_ASSISTANT, agent_message.final_response)

        return agent_message.final_response

