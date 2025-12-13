from datetime import timezone, datetime
from uuid import uuid4

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

class WorkspaceModel(Base):
    """
    CREATE TABLE public.workspaces (
	workspace_id uuid DEFAULT gen_random_uuid() NOT NULL,
	user_id int4 NULL,
	"name" varchar(255) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT workspaces_pkey PRIMARY KEY (workspace_id)
);
    -- public.workspaces foreign keys
    ALTER TABLE public.workspaces ADD CONSTRAINT
    workspaces_user_id_fkey FOREIGN KEY (user_id) REFERENCES
    public.users(user_id) ON DELETE CASCADE;
    """
    __tablename__ = 'workspaces'

    # Columns
    workspace_id = Column(UUID(as_uuid=True), primary_key=True, default=lambda:str(uuid4()))
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=True, server_default=func.now())

    # Indexes
    # none

    def __init__(self, user_id: Integer, name:str):
        self.user_id = user_id
        self.name = name
        self.created_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f"Workspace UserId={self.user_id} Name={self.name} CreationDate={self.created_at}"
    