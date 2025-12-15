import json
from datetime import datetime
from typing import Callable

from components.services.youtube_summary_bot import YouTubeSummaryBot
from components.services.youtube_service import YouTubeVideo, YouTubeService
from domain.models.agent_event import AgentEvent
from domain.repositories.video_repository import VideoRepository


class ChatApplication:

    def __init__(self, videos: list[YouTubeVideo] = [], on_event: Callable=None, video_repository: VideoRepository = None, workspace_id:str=None):
        self.youtube: YouTubeService = YouTubeService()
        self.summary_bot = YouTubeSummaryBot()
        self.videos = videos
        self.on_event = on_event
        self.video_repostory = video_repository
        self.workspace_id = workspace_id

    def watch_video(self, url) -> str:
        """returns a id, title of video, author"""

        video = self.youtube.get_video(url)
        self.videos.append(video)

        if self.video_repostory is None:
            id = len(self.videos) - 1
            return f"Watched {str(video)}. Id is {id}"
        else:

            record = {}
            record["url"] = video.url
            record["transcript"] = video.transcript
            record["title"] = video.title
            record["author"] = video.author
            db_id = self.video_repostory.save_video(self.workspace_id)
            return f"Watched {str(video)}. Transcript is available using the 'get_transcript' tool. The id is {db_id}"

        if self.on_event:
            ae = AgentEvent('video_watched', datetime.now().isoformat(), video.to_dict())
            self.on_event(ae)


    def list_videos(self) -> str:
        """returns a json with id, title of video, and author"""
        print(f"list_videos()")
        retval = []
        i = 0
        for video in self.videos:
            retval.append({
                "id": i,
                "video": str(video)
            })
            i += 1
        return json.dumps(retval, indent=2)

    def get_transcript(self, id) -> str:
        """returns the complete transcript of a video"""
        print(f"get_transcript{id}")
        return self.videos[int(id)].transcript

    def get_summary(self, id) -> str:
        """returns a summary of the video"""
        print(f"get_summary({id})")
        video = self.videos[int(id)]
        summary = self.summary_bot.summarize_transcript(video.transcript)
        if self.on_event:
            ae = AgentEvent('video_summarized', datetime.now().isoformat(), { 'summary': summary, 'video_id': 0 } )
            self.on_event(ae)
        return summary