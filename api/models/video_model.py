from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, Integer, Text, String, DateTime, Index,func

from .base import Base

class VideoModel(Base):
    __tablename__ = 'videos'

    # Columns
    video_id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    transcript = Column(Text, nullable=False)
    title = Column(String(500), nullable=False)
    channel = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True, server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_videos_url', 'url'),
    )

    def __init__(self, url:str, transcript:str, title:str, channel: str, summary: Optional[str] = None) -> None:
        self.url = url
        self.transcript = transcript
        self.title = title
        self.channel = channel
        self.summary = summary
        self.created_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        """debug string"""
        return f"VideoModel(id={self.video_id}, title='{self.title}')"