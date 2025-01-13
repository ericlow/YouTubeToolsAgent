import anthropic
import os
from datetime import datetime


def query_claude(self, system: str, message:str):
    client = anthropic.Anthropic()

    # Create the message
    print(os.environ.get('ANTHROPIC_API_KEY'))
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4096,
        temperature=0,
        system="You are an AI assistant that creates clear, concise summaries of video transcripts.",
        messages=[
            {
                "role": "user",
                "content": f"Please provide a concise summary of this video transcript, highlighting the key points and main takeaways:\n\n{transcript}"
            }
        ]
    )

    # Save the summary
    return message.content

def summarize_transcript(file_path):
    """
    Reads a transcript file and sends it to Claude for summarization
    """
    try:
        # Read the transcript file
        with open(file_path, 'r', encoding='utf-8') as f:
            transcript = f.read()

        output_file = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary[0].text)

        print(f"Summary saved to {output_file}")
        return summary

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

class SummaryBot:
    def __init__(self, mock:bool, claude: Claude):
        pass

    def summarize_transcript(self, transcript:str):
        if self.mock:
            return "summary from claude"
        else:
            return summarize_transcript(transcript)


if __name__ == "__main__":
    # You'll need to set your API key as an environment variable
    # export ANTHROPIC_API_KEY='your-api-key'
    transcript_file = "summaries/transcript.txt"
    summary = summarize_transcript(transcript_file)
    if summary:
        print("\nSummary:")
        print(summary)