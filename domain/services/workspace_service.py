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
from components.services.web_chat_appllcation import WebChatApplication
from components.services.youtube_service import YouTubeVideo
from domain.models.agent_event import AgentEvent
from domain.repositories.message_repository import MessageRepository
from domain.repositories.video_repository import VideoRepository, GetVideoArgs, GetVideoArgsUrl, \
    GetVideoArgsWorkspaceVideoId
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
    def __init__(self, message_repository:MessageRepository, video_repository:VideoRepository):
        self.message_repository = message_repository
        self.video_repository = video_repository
    def getMessages(self, workspace_id, cursor):
        return self.message_repository.get_messages(workspace_id)

    def send_message(self, workspace_id, message:str):

        def handle_event(event: AgentEvent):
            print(f"Message\nType:{event.type} \nMessage: {event.data}")
            if event.type in ('message','tool_use', 'tool_result'):
                self.message_repository.create_message(workspace_id,
                                                   MessageModel.ROLE_ASSISTANT,
                                                   event.data)
            elif event.type == 'video_watched':
                video = event.data
                # we are saving the video in the chatapplication. the chat application and the workspace service are fighting for control
#                self.video_repository.save_video(workspace_id, video)

            elif event.type == 'video_summarized':
                summary = event.data["summary"]
                video_id = event.data["video_id"]
                self.video_repository.save_summary(workspace_id, video_id, summary)
            else: # event type is unknown
                print(f'unknown event type{event.type}')

        # create + save message to send
        self.message_repository.create_message(workspace_id, MessageModel.ROLE_USER, message)

        # retrieve messages
        messages = self.message_repository.get_messages(workspace_id)
        agent_messages = [ChatMessage(Role(message.role), message.content) for message in messages]

        # retrieve videos
        videos = self.video_repository.get_videos(workspace_id=workspace_id)
        agent_context= [YouTubeVideo(url=video["url"], transcript=video["transcript"], title=video["title"], author=video["author"], publish_date="", video_duration=0) for video in videos]

        # Ask Agent to take next step
        agent = ChatAgent(agent_context, agent_messages, on_event=handle_event, workspace_id=workspace_id, video_repository=self.video_repository)
        agent_message = agent.chat(message)

        self.message_repository.create_message(workspace_id, MessageModel.ROLE_ASSISTANT, agent_message.final_response)

        return agent_message.final_response




