from dataclasses import dataclass
from typing import Literal


@dataclass
class AgentEvent:
    type: Literal['message','tool_use', 'tool_result']
    timestamp: str
    data: dict