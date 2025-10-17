import json

from components.services.youtube_summary_bot import YouTubeSummaryBot
from components.services.youtube_service import YouTubeVideo, YouTubeService


class ChatApplication:

    def __init__(self):
        self.youtube: YouTubeService = YouTubeService()
        self.videos: list[YouTubeVideo] = []
        self.summary_bot = YouTubeSummaryBot()

    def watch_video(self, url) -> str:
        """returns a id, title of video, author"""
        video = self.youtube.get_video(url)
        self.videos.append(video)
        id = len(self.videos) - 1
        return f"Watched {str(video)}. Id is {id}"

    def list_videos(self) -> str:
        """returns a json with id, title of video, and author"""
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
        return self.videos[int(id)].transcript

    def get_summary(self, id) -> str:
        """returns a summary of the video"""
        video = self.videos[int(id)]
        return self.summary_bot.summarize_transcript(video.transcript)