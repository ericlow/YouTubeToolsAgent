
TOOL_WATCH_VIDEO = "watch_video"
TOOL_LIST_VIDEOS = "list_videos"
TOOL_SUMMARIZE_VIDEO = "summarize_videos"
TOOL_GET_TRANSCRIPT = "get_transcript"

TOOLS = [
    {
        "name": TOOL_WATCH_VIDEO,
        "description": "Load a YouTube video by URL and extract its transcript.  The system caches the video in an enumerated collection, retrievable by the list_videos tool",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The YouTube video URL"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": TOOL_LIST_VIDEOS,
        "description": "List all currently loaded videos. Returns an enumerated list of previously watched videos",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": TOOL_SUMMARIZE_VIDEO,
        "description": "Generate a summary of a single, previously watched video. You should return this text, unmodified, if the user requests a summary.",
        "input_schema": {
            "type": "object",
            "properties": {
                "index": {
                    "type": "integer",
                    "description":"this is the index of the video. The index and video id can be retrieved from the list_videos tool"
                }
            },
            "required":["index"]
        }
    },
    {
        "name": TOOL_GET_TRANSCRIPT,
        "description": "Retrieve the transcript of a single video",
        "input_schema": {
            "type": "object",
            "properties": {
                "index": {
                    "type": "integer",
                    "description":"this is the index of the video. The index and video id can be retrieved from the list_videos tool"
                }
            },
            "required":["index"]
        }
    },
]