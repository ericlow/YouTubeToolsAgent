from components.anthropic.role import Role

class ChatMessage:
    def __init__(self, role: Role, content:str):
        self.role:Role = role
        self.content: str = content

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role.value,
            "content": self.content
        }