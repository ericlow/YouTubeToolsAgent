import json

from chat_appllcation import ChatApplication
from components.anthropic_service import ChatSession, ChatMessage, Role
from components.tool_executor import ToolExecutor
from components.tools import TOOLS


class ChatAgent:
    def __init__(self):
        self.tools = ToolExecutor(ChatApplication())

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
        self.session = ChatSession(self.prompt,[], TOOLS)

    def chat(self, message) -> str:
        chatMessage = ChatMessage(Role.USER, message)
        response = self.session.send(chatMessage)

        while True:
            if response.stop_reason != 'tool_use': break
            else:
                tool=response.content[1].name
                print("Tool Use:")
                print(response.content[0].text)
                print(f"tool:{tool}")
                print(json.dumps(response.content[1].input))
                tool_response = self.tools.execute_tool(tool,response.content[1].input)
                print(f"tool response: {tool_response}")
                response = self.session.send(ChatMessage(Role.USER,tool_response))

        print("Exit Loop")
        print(f"-> {response.content[0].text}")