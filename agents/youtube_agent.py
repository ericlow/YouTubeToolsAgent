from components.youtube_service import YouTubeService
from components.anthropic_service import YouTubeSummaryBot


class FilesystemAgentService:
    def __init__(self, mock:bool):
        self.mock = mock
    def watch(self, urls: str):
        if urls is not None or len(urls) > 0:
            youtube = YouTubeService(self.mock)

            list = urls.split(",")
            summaryBot = YouTubeSummaryBot(self.mock)
            videos = []
            for url in list:
                video = youtube.get_video(url.strip())
                youtube.save_transcript(video)

                word_count = 800 #video.video_duration

                summary = summaryBot.summarize_transcript(str(video), word_count)
                filename = summaryBot.save_to_disk(summary=summary, url=video.url, title=video.title)
                video.summary = summary
                video.filename = filename
                videos.append(video)

            master_summary = ""
            for video in videos:
                master_summary += f"{video.title}\n{video.summary}\n-------------"

#            insights = summaryBot.create_insights(master_summary)
 #           summaryBot.save_to_disk2(insights)

        else:
            # do we need a claude session? is claude api stateless?
            # claude should get a list of 10 videos worth watching via youtube search
            # claude should watch, then summarize all the videos
            # claude should decide what videos are worth summarizing
            # claude should create a summary of important videos
            youtube = YouTubeService(False)

            print(youtube.mock)
            list = urls.split(",")
            for url in list:
                # video = youtube.get_video(url)
                #
                # print(summary)
                pass


