import anthropic
import os
from datetime import datetime

class Claude:
    def __init__(self, model: str, max_tokens:int, temperature:0):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def query(self, system:str, message:str) -> str:
        # print(os.environ.get('ANTHROPIC_API_KEY'))
        client = anthropic.Anthropic()
        # Create the message
        response = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": f"{message}"
                }
            ]
        )

        # Save the summary
        return response.content[0].text

claude = Claude(model="claude-3-sonnet-20240229", max_tokens=4096, temperature=0)

"""
This bot creates summaries of youtube videos
"""
class YouTubeSummaryBot:

    def __init__(self, mock:bool):
        self.mock = True
        pass

    mock_summary = """
    Here is a concise summary of the key points and main takeaways from the video transcript:

    Introduction:
    - AI has the capabilities of creation (generating images, text, etc.), reasoning, and interacting in human-like ways. This presents massive business opportunities.
    - The AI transition is compared to the cloud transition, which unlocked new business models and applications. AI could replace services with software on an even larger scale.
    
    State of AI Today:
    - AI is already automating jobs like customer service and legal work. Software engineering with AI is becoming viable.
    - AI usage and revenue numbers look promising ($3B revenue in first year), but retention is still low compared to mobile apps. Smarter models are needed to meet expectations.
    - 2024 is expected to be the year AI moves from co-pilots to full agents taking humans out of the loop in some domains.
    
    Long-Term AI Impact:
    - AI is a productivity revolution that will drive significant cost reductions across industries like education and healthcare.
    - Concepts will be represented not as stored pixels but multi-dimensional models that capture context and meaning, mirroring human cognition.
    - Companies may eventually function like neural networks, with AI optimizing all processes in an interconnected way.
    - This could enable "one-person companies" to tackle more problems by leveraging AI capabilities.
    
    The audience (AI builders) will decide what's next and how to harness AI to increase productivity and create a better society.
    """
    def summarize_transcript(self, transcript:str) -> str:
        """
            creates a summary of a youtube transcript
        """
        print("\tSummarizing Video")
        if self.mock:
            return self.mock_summary
        else:
            system = "You are an AI assistant that creates clear, concise summaries of video transcripts."
            message = f"Please provide a concise summary of this video transcript, highlighting the key points and main takeaways:\n\n{transcript}"

            summary = claude.query(system=system, message=message)

            return summary


    def save_to_disk(self, summary: str, url: str, title: str) -> str:
        """
        Saves a transcript to file
        """
        try:
            # Read the transcript file
            #        with open(file_path, 'r', encoding='utf-8') as f:
            #            transcript = f.read()

            print(f"\tSaving transcript for \"{title}\" to disk")

            actual_string = summary.encode().decode('unicode-escape')

            output_file = f"summaries/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                content = f"{url}\n\n{title}\n\n{actual_string}"
                f.write(content)

            print(f"\tSummary saved to {output_file}")
            return output_file

        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def create_insights(self, transcripts:str) -> str:
        """
            creates insights from transcripts
        """
        print("\tCreating Insights")
        if self.mock:
            return "summary from claude"
        else:
            system = "You are an AI assistant that creates insights from summaries of several video transcripts."
            message = (f"I will provide the transcripts of several videos, listing the title, then the transcript. "
                       f"first, think about each transcript one by one, "
                       f"then create a viewpoint which provides insight about the current state, and the future. Reference"
                       f"important ideas by the video title which support predictions about the future:"
                       f"\n\n{transcripts}")


            summary = claude.query(system=system, message=message)

            return summary

    def save_to_disk2(self, insights) -> str:
        try:

            output_file = f"summaries/insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(insights)

            print(f"\tInsights saved to {output_file}")
            return output_file

        except Exception as e:
            print(f"Error: {str(e)}")
            return None
