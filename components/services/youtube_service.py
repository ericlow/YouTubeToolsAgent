import datetime
import os
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

from components.anthropic.anthropic_service import Content
from logger_config import getLogger

### Youtube video, this helps us to interact with a specific single video
class YouTubeVideo(Content):
    def __init__(self, url: str, transcript: str, title: str, author: str, publish_date: datetime,
                 video_duration:int):
        self.transcript = transcript
        self.title = title
        self.url = url
        self.author = author
        self.publish_date = publish_date
        self.video_duration = video_duration

        # Content interface
        self.source: str = self.url
        self.title: str = self.title
        self.author: str = self.author
        self.content: str = self.transcript
        self.creation_date: datetime = publish_date

    def __str__(self) -> str:
        return f"""URL: {self.url}\nTitle: {self.title}\nChannel: {self.author}\nPublish Date: {self.publish_date}"""
    def to_dict(self):
        return {
            'transcript': self.transcript,
            'title': self.title,
            'url': self.url,
            'author': self.author,
            'publish_date': self.publish_date,
            'video_duration': self.video_duration
        }



### YouTube Service that helps us to interact with youtube and the content (get video transcripts,
class YouTubeService:
    """This YouTubeService has methods to act on the YouTube API"""

    def __init__(self, mock: Optional[bool] = False):
        self.mock = mock
        self.logger = getLogger(__name__)
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=youtube_key)

    def get_video(self, url) -> YouTubeVideo:
        self.logger.debug(f"Retrieving video:{url}")
        if self.mock:
            path = Path(__file__).parent
            file_path = path / "transcript.txt"
            with open(file_path, 'r') as f:
                content = f.read()
            return YouTubeVideo(url=url, transcript="this is a transcript", title="mock video", author='mock author', publish_date=datetime.date.today(),video_duration=65)
        else:
            return get_video(url)

    def save_transcript(self, video: YouTubeVideo):
        filepath = f'summaries/transcript-{video.title}'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(video))
        self.logger.debug(f"Saved Transcript: {filepath}")

    def test(self):
        self.youtube.videoCategories().list(
            part="snippet",
            regionCode="US"
        )
        self.logger.info("YouTube OK")

### Helper functions

def get_video_id(url) -> int:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:be\/)([0-9A-Za-z_-]{11}).*'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            # return video id
            return match.group(1)
    # video id not found
    return None

def get_video_metadata(video_id: str) -> tuple[str, str, int, datetime]:
    YOUTUBE_KEY = os.getenv('YOUTUBE_API_KEY')
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

    response = youtube.videos().list(
        part='snippet,contentDetails',
        id=video_id
    ).execute()

    video = response['items'][0]
    return (
        video['snippet']['title'],
        video['snippet']['channelTitle'],
        video['contentDetails']['duration'],  # ISO 8601 format
        video['snippet']['publishedAt']
    )

    title = ''
    author = ''
    duration = 1234
    publish_date = datetime.date.today()
    return title, author, duration

def get_video_transcript(video_id: str) -> str:
    #transcript = YouTubeTranscriptApi.get_transcript(video_id)
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    return transcript

def get_video(url) -> YouTubeVideo:
    """Get video from YouTube url"""
    try:
        video_id = get_video_id(url)
        if not video_id:
            raise "Error: Could not extract video ID from URL"

        video_title, video_author, video_duration, publish_date = get_video_metadata(video_id)
        transcript = get_video_transcript(video_id)

        # Format transcript with timestamps
        formatted_transcript = f"Transcript for: {video_title}\n\n"
        for entry in transcript:

            timestamp = round(entry.start)
            minutes = timestamp // 60
            seconds = timestamp % 60
            line = f"[{minutes:02d}:{seconds:02d}] {entry.text}\n"
            formatted_transcript += line

        return YouTubeVideo(url=url, transcript=formatted_transcript, title=video_title, author=video_author,
                            publish_date=publish_date, video_duration=video_duration)

    except str:
        raise "Error: Could not extract video ID from URL"
    except TranscriptsDisabled:
        raise f"Error: Transcripts are disabled for this video.\nVideo Title: {video_title}"
    except NoTranscriptFound:
        raise f"Error: No transcript found for this video.\nVideo Title: {video_title}"
