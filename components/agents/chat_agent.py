import json
from typing import Any

from components.anthropic.chat_message import ChatMessage
from components.anthropic.chat_session import ChatSession
from components.anthropic.content import Content
from components.anthropic.role import Role
from components.services.chat_appllcation import ChatApplication
from domain.models.agent_result import AgentResult

from components.tool_executor import ToolExecutor
from components.tools import TOOLS
from logger_config import getLogger


class ChatAgent:
    def __init__(self, context: list[Content] = [], messages: list[ChatMessage]=[], tools:Any =TOOLS):
        self.tools = ToolExecutor(ChatApplication())
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
            
            # Communication Style
            You should keep responses under 300 words.  You should explain how you came to your conclusion and
            what tools you decided to use and why you chose your tools.  The explanation of tool use can be an 
            additional 500 words and is not counted against the original response.
            
            # Error handling guidance
            You can refuse or indicate the user has asked for something impossible or the tool did not work as
            expected.  There are no limitations on reporting errors.
             
        """
        self.session = ChatSession(self.prompt, tools=tools, context=context, messages=messages)

    def chat(self, message:str) -> AgentResult:
        chatMessage = ChatMessage(Role.USER, message)
        response = self.session.send(chatMessage)

        while True:
            if response.stop_reason != 'tool_use': break
            else:
                tool=response.content[1].name
                self.logger.debug("Tool Use:")
                self.logger.debug(response.content[0].text)
                self.logger.debug(f"tool:{tool}")
                self.logger.debug(json.dumps(response.content[1].input))
                tool_response = self.tools.execute_tool(tool,response.content[1].input)
                self.logger.debug(f"tool response: {tool_response}")
                response = self.session.send(ChatMessage(Role.USER,tool_response))

        exit_message = response.content[0].text
        self.logger.debug(f"-> {exit_message}")

        # Return AgentResult with all messages and final response
        return AgentResult(
            all_messages=self.session.messages,
            final_response=exit_message
        )
    def is_healthy(self) -> bool:
        return self.session.is_healthy()