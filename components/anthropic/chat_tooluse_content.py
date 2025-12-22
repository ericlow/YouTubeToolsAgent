from typing import Any

class ToolUseContent:
    def __init__(self, tool_use_id: str, content: Any):
        self.tool_use_id = tool_use_id
        self.content = content

    def to_dict(self):
        """
        Returns:
            array in this form:
              [
                  {
                      "type": "tool_result",
                      "tool_use_id": tool_use_id,
                      "content": result
                  }
              ]

            this will be fed directly to the content field in an anthropic message
        """
        return [
            {
                "type": "tool_result",
                "tool_use_id": self.tool_use_id,
                "content": self.content
            }
        ]

