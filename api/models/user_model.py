from datetime import timezone, datetime

from sqlalchemy import Column, Integer, DateTime

from .base import Base

class UserModel(Base):
    """
    CREATE TABLE public.users (
    	user_id serial4 NOT NULL,
    	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
    	CONSTRAINT users_pkey PRIMARY KEY (user_id)
    );
    """
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable = False)

    def __init__(self):
        self.created_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        """debug string"""
        return f"User(id={self.user_id}, created_at={self.created_at}')"