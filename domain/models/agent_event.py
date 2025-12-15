from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class AgentEvent:
    type: Literal['message','tool_use', 'tool_result', 'video_watched', 'video_summarized']
    timestamp: str
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
