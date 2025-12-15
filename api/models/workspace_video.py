from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base

class WorkspaceVideoModel(Base):
    """
    CREATE TABLE public.workspace_videos (
        workspace_id uuid NOT NULL,
        video_id int4 NOT NULL,
        added_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
        CONSTRAINT workspace_videos_pkey PRIMARY KEY (workspace_id, video_id)
    );
-- public.workspace_videos foreign keys

ALTER TABLE public.workspace_videos ADD CONSTRAINT workspace_videos_video_id_fkey FOREIGN KEY (video_id) REFERENCES public.videos(video_id) ON DELETE CASCADE;
ALTER TABLE public.workspace_videos ADD CONSTRAINT workspace_videos_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES public.workspaces(workspace_id) ON DELETE CASCADE;
    """
    __tablename__ = 'workspace_videos'

    # Columns
    # these two foreign keys marked both as primary keys represent a natural composite key
    workspace_id = Column(UUID(as_uuid=True),ForeignKey('workspaces.workspace_id'), primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.video_id'), primary_key=True)
    added_at = Column(DateTime, nullable=False, server_default=func.now())
    summary = Column(Text, nullable=True)

    # Indexes
    # none

    # Relationships
    video = relationship("VideoModel")

    def __init__(self, workspace_id:str, video_id:Integer, summary:str=None):
        self.workspace_id = workspace_id
        self.video_id = video_id
        self.added_at = datetime.now(timezone.utc)
        self.summary = summary

    def to_dict(self):
        return {
            'video_id': self.video_id,
            'url': self.video.url,
            'transcript': self.video.transcript,
            'title': self.video.title,
            'author': self.video.channel,
            'summary': self.summary  # From junction table now
        }
