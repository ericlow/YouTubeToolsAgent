from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from pytubefix import YouTube
import re

class YouTubeVideo:
    def __init__(self, url:str, transcript:str, title:str):
        self.transcript = transcript
        self.title = title
        self.url = url
class YouTubeService:
    """This YouTubeService has methods to act on the YouTube API"""
    def __init__(self, mock:bool):
        self.mock = mock
    def get_video(self, url) -> YouTubeVideo:
        print (f"Retrieving video:{url}")
        if self.mock:
            return YouTubeVideo(url=url, transcript="this is a transcript", title="mock video")
        else:
            return get_video(url)
def get_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:be\/)([0-9A-Za-z_-]{11}).*'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video(url) -> YouTubeVideo:
    """Get transcript from YouTube video"""
    try:
        # Extract video ID
        video_id = get_video_id(url)
        if not video_id:
            raise "Error: Could not extract video ID from URL"

        try:
            yt = YouTube(url)
            video_title = yt.title
        except Exception as e:
            print(f"Warning: Could not get video title. Error: {str(e)}")
            video_title = "Unknown Title"

        # Check if video is or was a livestream
        if yt is not None and yt.vid_info and 'isLiveContent' in yt.vid_info.get('videoDetails', {}):
            is_live_content = yt.vid_info['videoDetails']['isLiveContent']
            if is_live_content:
                raise f"Error: This appears to be a livestream or stream replay. Transcripts may not be available for this type of content.\nVideo Title: {video_title}"

        # Try to get transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except TranscriptsDisabled:
            raise f"Error: Transcripts are disabled for this video.\nVideo Title: {video_title}"
        except NoTranscriptFound:
            raise f"Error: No transcript found for this video.\nVideo Title: {video_title}"

        # Format transcript with timestamps
        formatted_transcript = f"Transcript for: {video_title}\n\n"
        for entry in transcript:
            timestamp = int(entry['start'])
            minutes = timestamp // 60
            seconds = timestamp % 60
            formatted_transcript += f"[{minutes:02d}:{seconds:02d}] {entry['text']}\n"

        return YouTubeVideo(url=url, transcript=formatted_transcript, title=video_title, author=author, publish_date=publish_date)


    except Exception as e:
        raise e

# Example usage
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=xF554Tlzo-c"
#    save_transcript(url, "summaries/transcript.txt")