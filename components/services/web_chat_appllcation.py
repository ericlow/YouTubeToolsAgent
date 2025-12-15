import json
from datetime import datetime
from typing import Callable

from components.services.chat_appllcation import ChatApplication
from components.services.youtube_summary_bot import YouTubeSummaryBot
from components.services.youtube_service import YouTubeVideo, YouTubeService
from domain.models.agent_event import AgentEvent
from domain.repositories.video_repository import VideoRepository, GetVideoArgsUrl, GetVideoArgsWorkspaceVideoId


class WebChatApplication(ChatApplication):

    def __init__(self, on_event: Callable=None, video_repository: VideoRepository = None, workspace_id:str=None):
        self.youtube: YouTubeService = YouTubeService()
        self.summary_bot = YouTubeSummaryBot()
        self.on_event = on_event
        self.video_repostory = video_repository
        self.workspace_id = workspace_id

    def watch_video(self, url) -> str:
        """returns a id, title of video, author"""

        # video not watched
        # video watched but not in workspace
        # video watched and in workspace

        # video watched at all?
        getVideoArgs = GetVideoArgsUrl(url)
        record = self.video_repostory.get_video(getVideoArgs)
        if record is None:
            # YouTube bans users who make too many API Calls.  Only call Youtube when necessary!
            video = self.youtube.get_video(url)

            record = {}
            record["url"] = video.url
            record["transcript"] = video.transcript
            record["title"] = video.title
            record["author"] = video.author

        db_id = self.video_repostory.save_video(self.workspace_id, record)
        videodict = video.to_dict()
        if self.on_event:
            ae = AgentEvent('video_watched', datetime.now().isoformat(), videodict)
            self.on_event(ae)

        return f"Watched {str(video)}, transcript can be retrieved with the get_transcript tool.  The id is {db_id}"

    def list_videos(self) -> str:
        """returns a json with id, title of video, and author"""
        print(f"list_videos()")
        videos = self.video_repostory.get_videos(self.workspace_id)
        return json.dumps(videos, indent=2)

    def get_transcript(self, id:int) -> str:
        """returns the complete transcript of a video"""
        print(f"get_transcript{id}")
        video = self.video_repostory.get_video(self.workspace_id, id)
        return video["transcript"]

    def get_summary(self, id:int) -> str:
        """returns a summary of the video"""
        print(f"get_summary({id})")
        getVideoArgs = GetVideoArgsWorkspaceVideoId(self.workspace_id, id)
        video = self.video_repostory.get_video(getVideoArgs)
        summary = self.summary_bot.summarize_transcript(video["transcript"])
        if self.on_event:
            ae = AgentEvent('video_summarized', datetime.now().isoformat(), { 'summary': summary, 'video_id': video["video_id"] } )
            self.on_event(ae)
        return summary