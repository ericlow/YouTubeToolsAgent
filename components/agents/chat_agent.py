import json
from datetime import datetime
from typing import Any

from anthropic.types import ToolUseBlock, Message

from components.anthropic.chat_message import ChatMessage
from components.anthropic.chat_session import ChatSession
from components.anthropic.content import Content
from components.anthropic.role import Role
from components.services.chat_appllcation import ChatApplication
from components.services.web_chat_appllcation import WebChatApplication
from domain.models.agent_event import AgentEvent
from domain.models.agent_result import AgentResult

from components.tool_executor import ToolExecutor
from components.tools import TOOLS
from domain.repositories.video_repository import VideoRepository
from logger_config import getLogger


class ChatAgent:
    def __init__(self, context: list[Content] = [], messages: list[ChatMessage]=[], tools:Any =TOOLS, on_event=None, workspace_id:int= 0, video_repository: VideoRepository=None):

        self.on_event = on_event
        self.tools = ToolExecutor(WebChatApplication(on_event=on_event, video_repository=video_repository, workspace_id=workspace_id))
        self.logger = getLogger(__name__)
        self.prompt = """
            # Role
            You are a YouTube content analyzer.  You will use the tools provided to watch videos, summarize,
            analyze, answer questions, and perform other text based activities.
            
            # Core Capabilities
            refer to the tools definition. The basic capabilities are that you can watch videos, get a list of
            videos watched, get summaries, and get full transcripts.
            
            # Tool Use Guidelines
            You can use the tools without asking.  If there is uncertainty about how to use the tools or what
            they do, their role, or any other questions about the tools that is not adequately addressed in the
            tool description, you can proactively ask questions at any time.
            
            When you use summarize_videos tool, the result is already a final summary ready for the user.
            Do not re-summarize or reprocess the summary - present it directly.
            
            # Communication Style
            You should keep responses under 300 words.  You should explain how you came to your conclusion and
            what tools you decided to use and why you chose your tools.  The explanation of tool use can be an 
            additional 500 words and is not counted against the original response.
            
            # Error handling guidance
            You can refuse or indicate the user has asked for something impossible or the tool did not work as
            expected.  There are no limitations on reporting errors.
            
             
        """
        self.session = ChatSession(self.prompt, tools=tools, context=context, messages=messages)


    def print_response(self, response:Message):
        print(f"\tResponse")
        print(f"\t\tstop reason: {response.stop_reason}")
        print(f"\t\ttype: {response.type}")
        print(f"\t\tcontent")
        i = 0
        for item in response.content:
            print(f"\t\t\titem: {i}")
            i+=1
            print(f"\t\t\tType: {item.type}")
            print(f"\t\t\t{item.to_dict()}")


    def chat(self, message:str) -> AgentResult:
        chatMessage = ChatMessage(Role.USER, message)
        print(f"chat: {message}")
        response = self.session.send(chatMessage)
        self.print_response(response)
        ae = AgentEvent(AgentEvent.to_agent_event_type(response.stop_reason), datetime.now().isoformat(), response.content[0].text)
        if self.on_event: self.on_event(ae)

        while True:
            if response.stop_reason != 'tool_use': break
            else:

                # HACK ELOW somtimes we have 2 content, sometimes 1, sometimes its a ToolUseBlock, sometimes it's something else....
                print("Tool Use ->")
                toolblock=next((item for item in response.content if item.type =='tool_use'),None)
                tool = toolblock.name
                input = toolblock.input
                tool_response = self.tools.execute_tool(tool, input)
                print(f"\tTool Use Result: {tool_response}")
                response = self.session.send(ChatMessage(Role.ASSISTANT,tool_response))
                self.print_response(response)

                # ae = AgentEvent('tool_result', datetime.now() ,event_detail)
                # if self.on_event: self.on_event(ae)
        exit_message = json.dumps(response.to_dict())
        if response.content is None:
            print("response.content is None")
        elif len(response.content) == 0:
            print("response.content is 0 len")
        elif len(response.content) > 1:
            self.print_response(response)
        elif not hasattr(response.content[0], 'text'):
            print("response.content[0] has unexpected type")
        else:
            exit_message = response.content[0].text
        self.logger.debug(f"tool exit messsage: {exit_message}")

        # Return AgentResult with all messages and final response
        return AgentResult(
            all_messages=self.session.messages,
            final_response=exit_message
        )
    def is_healthy(self) -> bool:
        return self.session.is_healthy()