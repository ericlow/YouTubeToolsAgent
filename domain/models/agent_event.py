from dataclasses import dataclass
from typing import Literal

from anthropic.types import Message


@dataclass
class AgentEvent:
    type: Literal['message','tool_use', 'tool_result', 'video_watched', 'video_summarized']
    timestamp: str

    """
        dictionary form of a Message / Response object
    """
    data: dict

    @staticmethod
    def to_agent_event_type(stop_reason:str):
        match stop_reason:
            case 'tool_use':
                return 'tool_use'
            case 'end_turn':
                return 'message'
            case _ :
                print(f"AgentEvent.to_agent_event_type: unexpected Type{stop_reason}")
                # 'max_tokens'
                return stop_reason

    @staticmethod
    def response_to_dict(response: Message):
        retval = dict()
        retval["role"] = response.role
        retval["content"] = [c.model_dump() for c in response.content]
        return retval