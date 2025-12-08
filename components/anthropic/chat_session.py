from typing import Any

from anthropic import Stream
from anthropic.types import Message, RawMessageStreamEvent

from components.anthropic.anthropic_service import Claude
from components.anthropic.chat_message import ChatMessage
from components.anthropic.content import Content
from components.anthropic.role import Role

"""
    Claude chat session.  It collects resources such as the prompt and content, as well as tools, and the message history. 
    The prompt and content can be used as the system prompt and can be collected and cached together.
"""
class ChatSession:
    def __init__(self, prompt: str, context: list[Content] = [], tools:Any =[]):
        self.claude:Claude = Claude()
        self.prompt: str = prompt
        self.context: list[Content] | [] = context
        self.system:  list[dict[str, Any]] = self.update_context(context)
        self.messages: list[dict[str,str]] = []
        self.tools: Any = tools

    def update_context(self, context:list[Content]):
        self.system  = Claude.create_system_prompt(self.prompt, context)
        return self.system

    def send(self, message :ChatMessage) -> Message | Stream[RawMessageStreamEvent]:
        self.messages.append(message.to_dict())

        rawresponse = self.claude.query_adv(self.system, self.messages,tools = self.tools)
        message = rawresponse.content[0].text
        response = ChatMessage(Role.ASSISTANT, message)
        self.messages.append(response.to_dict())

        return rawresponse
    def is_healthy(self):
        return self.claude.is_healthy()