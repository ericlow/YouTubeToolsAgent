from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

"""
Workspace Entity - Aggregate Root

A workspace represents a user's collection of videos and their chat history.
This is the aggregate root that controls access to videos and messages.
"""
class Workspace:
    """
    Workspace Aggregate Root.

    Business Rules (Invariants):
    - Must have a name
    - Must belong to a user
    - Can have zero or more videos
    - Messages belong to this workspace (die with workspace)
    - Same video cannot be added twice
    """
    def __init__(self,
                name:str,
                user_id: int,
                workspace_id: Optional[UUID] = None,
                created_at: Optional[datetime]= None
                ):
        """
        Args:
            name: workspace name (required)
            user_id: owner of workspace (required)
            workspace_id: (generated if not provided)
            created_at: (now, if not provided)
        """

        # Enforce invariants
        if not name or not name.strip():
            raise ValueError("Workspace name cannot be empty")
        if user_id is None or user_id <= 0:
            raise ValueError("Workspace must belong to a valid user")

        # Identity
        self._workspace_id = workspace_id or uuid4()

        # Properties
        self._name = name.strip()
        self._user_id = user_id
        self._created_at = created_at or datetime.utcnow()

        # Collections
        self._video_references: List[int] = []  # Video IDs only
        self._messages:List = []

    # Properties - Read-only access to internal state

    @property
    def workspace_id(self) -> UUID:
        """Unique identifier for this workspace."""
        return self._workspace_id

    @property
    def name(self) -> str:
        """Workspace name."""
        return self._name

    @property
    def user_id(self) -> int:
        """ID of user who owns this workspace."""
        return self._user_id

    @property
    def created_at(self) -> datetime:
        """When this workspace was created."""
        return self._created_at

    @property
    def video_ids(self) -> List[int]:
        """List of video IDs in this workspace (copy for safety)."""
        return self._video_references.copy()

    @property
    def messages(self):  # -> List[Message]
        """List of messages in this workspace (copy for safety)."""
        return self._messages.copy()

    @property
    def video_count(self) -> int:
        """Number of videos in this workspace."""
        return len(self._video_references)

    @property
    def message_count(self) -> int:
        """Number of messages in this workspace."""
        return len(self._messages)

    # Business Logic - Behavior

    def add_video_reference(self, video_id: int) -> None:
        """
        Add a reference to a video in this workspace.

        Args:
            video_id: ID of the video to add

        Raises:
            ValueError: If video already exists in workspace
        """
        if video_id in self._video_references:
            raise ValueError(f"Video {video_id} already exists in workspace")

        self._video_references.append(video_id)

    def remove_video_reference(self, video_id: int) -> None:
        """
        Remove a video reference from this workspace.

        Args:
            video_id: ID of the video to remove

        Raises:
            ValueError: If video not in workspace
        """
        if video_id not in self._video_references:
            raise ValueError(f"Video {video_id} not in workspace")

        self._video_references.remove(video_id)

    def has_video(self, video_id: int) -> bool:
        """Check if a video is in this workspace."""
        return video_id in self._video_references

    def add_message(self, message) -> None:  # message: Message
        """
        Add a message to this workspace's conversation.

        Args:
            message: Message value object to add
        """
        # Business rule: If message references a video, video must be in workspace
        if hasattr(message, 'video_id') and message.video_id is not None:
            if not self.has_video(message.video_id):
                raise ValueError(
                    f"Cannot add message about video {message.video_id} - "
                    "video not in workspace"
                )

        self._messages.append(message)

    def get_conversation_context(self, limit: int = 50) -> List:  # -> List[Message]
        """
        Get recent messages for LLM context.

        Args:
            limit: Maximum number of recent messages to return

        Returns:
            List of most recent messages (newest last)
        """
        if limit <= 0:
            raise ValueError("Limit must be positive")

        return self._messages[-limit:]

    def get_messages_about_video(self, video_id: int) -> List:  # -> List[Message]
        """
        Get all messages related to a specific video.

        Args:
            video_id: ID of the video

        Returns:
            List of messages that reference this video
        """
        if not self.has_video(video_id):
            raise ValueError(f"Video {video_id} not in workspace")

        return [
            msg for msg in self._messages
            if hasattr(msg, 'video_id') and msg.video_id == video_id
        ]