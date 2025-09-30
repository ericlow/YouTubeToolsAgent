import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

class YouTubeVideo:
    def __init__(self, url: str, transcript: str, title: str, author: str, publish_date: datetime,
                 video_duration:int):
        self.transcript = transcript
        self.title = title
        self.url = url
        self.author = author
        self.publish_date = publish_date
        self.video_duration = video_duration

    def __str__(self) -> str:
        return f"""URL: {self.url}\nTitle: {self.title}\nChannel: {self.author}\nPublish Date: {self.publish_date}\n\n{self.transcript}"""


class YouTubeService:
    """This YouTubeService has methods to act on the YouTube API"""

    def __init__(self, mock: bool):
        self.mock = mock

    def get_video(self, url) -> YouTubeVideo:
        print(f"Retrieving video:{url}")
        if self.mock:
            return YouTubeVideo(url=url, transcript="this is a transcript", title="mock video", author='mock author', publish_date=datetime.date.today(),video_duration=65)
        else:
            return get_video(url)

    def save_transcript(self, video: YouTubeVideo):
        filepath = f'summaries/transcript-{video.title}'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(video))
        print(f"Saved Transcript: {filepath}")

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

    youtube = build('youtube', 'v3', developerKey='AIzaSyChPGU5Un9dbWdA5lupHL8zbIJNyGMOHwk')

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
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
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
            timestamp = int(entry['start'])
            minutes = timestamp // 60
            seconds = timestamp % 60
            formatted_transcript += f"[{minutes:02d}:{seconds:02d}] {entry['text']}\n"

        return YouTubeVideo(url=url, transcript=formatted_transcript, title=video_title, author=video_author,
                            publish_date=publish_date, video_duration=video_duration)

    except str:
        raise "Error: Could not extract video ID from URL"
    except TranscriptsDisabled:
        raise f"Error: Transcripts are disabled for this video.\nVideo Title: {video_title}"
    except NoTranscriptFound:
        raise f"Error: No transcript found for this video.\nVideo Title: {video_title}"


# Example usage
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=xF554Tlzo-c"
#    save_transcript(url, "summaries/transcript.txt")
