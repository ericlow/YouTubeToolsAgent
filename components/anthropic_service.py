import os
from datetime import datetime
from enum import Enum
from typing import Any, Protocol
import anthropic
from anthropic import Anthropic

class Content(Protocol):
    source: str
    title: str
    author: str
    content: str
    creation_date: datetime

class Claude:

    MODEL_OPUS_4_1 ="claude-opus-4-1-20250805"      # $15   / MTOK
    MODEL_SONNET_4_5 = "claude-sonnet-4-5-20250929" # $3    / MTOK
    MODEL_HAIKU = "claude-3-5-haiku-20241022"       # $0.80 / MTOK

    MODEL_DEFAULT = MODEL_HAIKU

    def __init__(self, model: str = MODEL_DEFAULT, max_tokens:int=8192, creativity:float = 0):
        """
        Constructor
        Args:
            model: name of model
                https://docs.anthropic.com/en/docs/about-claude/models
            max_tokens: max number of tokens in response
            creativity:
                0: More focused, deterministic, and consistent responses. Claude will tend to choose the most likely/probable next tokens. This is great for:
                    Factual questions
                    Code generation
                    Data analysis
                    Tasks requiring high accuracy

                1: More creative, varied, and exploratory responses. Claude will be more likely to choose less probable tokens. This works well for:
                    Creative writing
                    Brainstorming
                    Generating multiple different approaches
                    More conversational interactions
        """
        self.model:str = model
        self.max_tokens: int = max_tokens
        self.temperature: float = creativity
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')

        self.client: Anthropic = anthropic.Anthropic(api_key=anthropic_key)
        self.system_prompt: list[dict[str,Any]] | None = None

    def query(self, system:str, message:str) -> str:

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": f"{message}"
                }
            ]
        )

        return response.content[0].text
    def query_basic(self, system: str, message:list[dict[str,str]]) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system,
            messages=message
        )

        return response.content[0].text

    def is_healthy(self):
        try:
            self.client.models.list()
            print("Claude OK")
            return True
        except anthropic.AnthropicError as e:
            print("Claude Error")
            print(e)
            return False

    def create_system_prompt(prompt:str, contentlist: list[Content]) -> list[dict[str, Any]]:
        system_blocks = []
        if len(prompt) > 0:
            system_blocks.append({
                "type":"text",
                "text": prompt
                # no caching, prompts are too small and there is no benefit
            })

        for content in contentlist:
            block = {
                "type":"text",
                "text":f"""
                    creation date: {content.creation_date}
                    source:{content.source}
                    author:{content.author}
                    title:{content.title}
                    content:{content.content}
                """,
                # using caching because the content is expected to be large, cache is 5 mins.
               "cache_control":{"type": "ephemeral"}

            }
            system_blocks.append(block)

        return system_blocks


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage:
    def __init__(self, role: Role, content:str):
        self.role:Role = role
        self.content: str = content
    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role.value,
            "content": self.content
        }

class ChatSession:
    def __init__(self, prompt: str, context: list[Content] = None):
        self.claude:Claude = Claude()
        self.prompt: str = prompt
        self.context: list[Content] | None = context
        self.system:  list[dict[str, Any]] = self.update_context(context)
        self.messages: list[dict[str,str]] = []

    def update_context(self, context:list[Content]):
        self.system  = Claude.create_system_prompt(self.prompt, context)

    def send(self, message :ChatMessage) -> str:
        self.messages.append(message.to_dict())
        message = self.claude.query_basic(self.system, self.messages)
        response = ChatMessage(Role.ASSISTANT, message)
        self.messages.append(response.to_dict())
        return message