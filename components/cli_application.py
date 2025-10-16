from typing import Dict

from components.anthropic.anthropic_service import Claude
from components.anthropic.chat_message import ChatMessage
from components.anthropic.chat_session import ChatSession
from components.anthropic.role import Role
from components.bots.youtube_summary_bot import YouTubeSummaryBot
from components.youtube_service import YouTubeVideo, YouTubeService


class CliApplication:

    def __init__(self):
        # self.video_counter = 0
        # we create a separate counter because id depends on number of vids.  But if
        # we delete a video, there is a way to reuse an id
        self.videos : Dict[int, YouTubeVideo] = {}
        self.video_counter = 0
        self.claude = Claude()
        self.prompt = """You are a conversation bot that will have conversations around content provided to you."""
        self.chatsession = ChatSession(self.prompt, [])

    def watch_video(self, url) -> str:
        youtube = YouTubeService()

        video = youtube.get_video(url)
        self.videos[self.video_counter] = video
        self.video_counter += 1
        self.chatsession.update_context(list(self.videos.values()))
        return str(video)

    def ask_question(self, id, question):
        message = ChatMessage(Role.USER, question)
        response = self.chatsession.send(message)
        print(response)


    def save_transcript(self, id, filename):
        video = self.videos[id]
        with open(filename, 'w') as f:
            f.write(video.transcript)

    def summarize_video(self, id):
        bot = YouTubeSummaryBot(False)
        if id == -1:
            video = self.videos[len(self.videos)-1]
        else:
            video = self.videos[id]
        summary = bot.summarize_transcript(video.transcript, 300)

        print(summary)

    def list_all_videos(self) -> str:
        retval = ""
        for video_id in self.videos:
            video = self.videos[video_id]
            retval += f"{video_id}\t{video.author}\t{video.title}\n"
        return retval

    def do_test(self):
        youtube = YouTubeService()
        youtube.test()
        claude = Claude()
        r = claude.is_healthy()
        print("Tests complete")