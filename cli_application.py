from typing import Dict

from components.anthropic_service import YouTubeSummaryBot
from components.youtube_service import YouTubeVideo, YouTubeService


class CliApplication:

    def __init__(self):
        # self.video_counter = 0
        # we create a separate counter because id depends on number of vids.  But if
        # we delete a video, there is a way to reuse an id
        self.videos : Dict[int, YouTubeVideo] = {}
        self.video_counter = 0

    def watch_video(self, url):
        youtube = YouTubeService()
        #YOUTUBE_URL = "https://www.youtube.com/watch?v=Nrh9EGVk45s"
        video = youtube.get_video(url)
        self.videos[self.video_counter] = video
        self.video_counter += 1

    def ask_question(self, id, question):
        pass

    def save_transcript(self, id, filename):
        video = self.videos[id]
        with open(filename, 'w') as f:
            f.write(video.transcript)

    def summarize_video(self, id):
        bot = YouTubeSummaryBot(False)
        video = self.videos[id]
        summary = bot.summarize_transcript(video.transcript, 300)
        print(summary)

    def list_all_videos(self) -> str:
        retval = ""
        for video_id in self.videos:
            video = self.videos[video_id]
            retval += f"{video_id}\t{video.author}\t{video.title}\n"
        return retval


