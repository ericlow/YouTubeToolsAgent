from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, func, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class MessageModel(Base):
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspaces.workspace_id'), nullable = False)
    role = Column(String(20), nullable = False)
    content = Column(Text, nullable  = False)
    created_at = Column(DateTime, nullable = True, server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_messages_created_at', 'created_at'),
        Index('idx_messages_workspace_id', 'workspace_id'),
    )

    def __init__(self, workspace_id: str, role:str, content: str):
        self.workspace_id = workspace_id
        self.role = role
        self.content = content
        self.created_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f"MessageModel Id={self.message_id} WorkspaceId={self.workspace_id} Role={self.role} Content={self.content}"
