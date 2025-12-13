from dataclasses import dataclass


@dataclass
class AgentResult:
    """
    Result of agent execution containing all messages and the final response.

    This is a minimal version for Vertical Slice 1 (messages only).
    Will be extended in Slice 2 to include videos_watched.
    """
    all_messages: list[dict]  # User, assistant, tool_use, tool_result messages
    final_response: str        # The text response shown to user
