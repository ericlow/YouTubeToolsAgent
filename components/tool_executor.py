from typing import Any

from components.services.chat_appllcation import ChatApplication
from components.tools import *

class ToolExecutor:
    def __init__(self, application: ChatApplication):
        self.app = application

    def execute_tool(self, tool_name: str, tool_input:dict[str, Any]) -> str:
        """execute a tool and return the result as a string"""
        if tool_name == TOOL_WATCH_VIDEO:
            url = tool_input["url"]
            return self.app.watch_video(url)

        if tool_name == TOOL_SUMMARIZE_VIDEO:
            index = tool_input["id"]
            return self.app.get_summary(index)

        if tool_name == TOOL_LIST_VIDEOS:
            return self.app.list_videos()

        if tool_name == TOOL_GET_TRANSCRIPT:
            index = tool_input["id"]
            return self.app.get_transcript(index)

        if tool_name == TOOL_SUMMARIZE_VIDEO:
            index = tool_input["id"]
            return self.app.get_summary(index)
