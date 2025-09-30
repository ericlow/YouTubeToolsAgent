import anthropic
import os
from datetime import datetime

class Claude:
    def __init__(self, model: str, max_tokens:int, creativity:0):
        """
        Constructor
        Args:
            model: name of model
                https://docs.anthropic.com/en/docs/about-claude/models
            max_tokens: max number of tokens in response
            creativity:
                0: More focused, deterministic, and consistent responses. Claude will tend to choose the most likely/probable next tokens. This is great for:
                    Factual questions
                    Code generation
                    Data analysis
                    Tasks requiring high accuracy

                1: More creative, varied, and exploratory responses. Claude will be more likely to choose less probable tokens. This works well for:
                    Creative writing
                    Brainstorming
                    Generating multiple different approaches
                    More conversational interactions
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = creativity

    def query(self, system:str, message:str) -> str:

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

#claude = Claude(model="claude-3-sonnet-20240229", max_tokens=4096, creativity=0)
claude = Claude(model="claude-3-5-sonnet-20241022", max_tokens=8192, creativity=0)

"""
This bot creates summaries of youtube videos
"""
class YouTubeSummaryBot:

    def __init__(self, mock:bool):
        self.mock = mock
        pass

    mock_summary = """
    Here is a MOCK summary of the key points and main takeaways from the video transcript:

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
    def summarize_transcript(self, transcript:str, word_count: int) -> str:
        """
            creates a summary of a youtube transcript
        """
        print("\tSummarizing Video")
        if self.mock:
            return self.mock_summary
        else:
            system = "You are an AI assistant that creates summaries of video transcripts."
#            message = f"Speakers: Please analyze this transcript and identify the speakers with high confidence. For each speaker you identify with certainty, provide: 1. Name 2. a short biography.  Only include speakers and names that can be identified with high confidence from the transcript. If no speakers can be determined, do not create this section.  Summary: Create a summary which is approximately {word_count} words. highlight the key points and main takeaways.  Key Points A bulleted list of list the timestamps of key points, and a sentence describing the key point Quotes A bulleted list of important quotes, if any, and a timestamp where it can be found.:\n\n{transcript}"
            message_summarize = f"Summarize this video.:\n\n{transcript}"
            message = f"First: Speakers: Please analyze this transcript and identify the speakers with high confidence. Only include speakers and names that can be identified with high confidence from the transcript. For each speaker you identify with certainty, provide: 1. Name 2. a short biography. Second: Summarize this video.:\n\n{transcript}"
#            message = f"Speakers: Please analyze this transcript and identify the speakers with high confidence. For each speaker you identify with certainty, provide: 1. Name 2. a short biography.  Only include speakers and names that can be identified with high confidence from the transcript. If no speakers can be determined, do not create this section. highlight the key points and main takeaways.  Key Points A bulleted list of list the timestamps of key points, and a sentence describing the key point Quotes A bulleted list of important quotes, if any, and a timestamp where it can be found.\n\n{transcript}"
            message = f"""
                        You are an AI assistant specialized in analyzing and summarizing video transcripts. 
                        Your task is to carefully examine the provided transcript, identify speakers with high confidence, 
                        and create a summary of the video content.
                        
                        Here is the video transcript you need to analyze:
                        {transcript}                    
                        Please follow these steps:
                        
                        1. Speaker Identification:
                           - Analyze the transcript, and consider the Channel name, and identify speakers with high confidence.
                           - Only include speakers and names that can be clearly identified from the transcript.
                           - For each speaker you identify with certainty, provide:
                             a) Their name
                             b) A short biography (1-3 sentences)
                        
                        2. Video Summary:
                           - Create a summary of the video content.
                           - Focus on the main topics, key points, and any significant conclusions or outcomes discussed.
                        
                        3. Key Learnings:
                            - create a list of key learnings and insights from the video
                            
                        Before providing your final output, wrap your analysis inside <transcript_analysis> tags. This should include:
                        - Your reasoning for identifying specific speakers, including direct quotes from the transcript that support your identification
                        - A list of all potential topics discussed in the video
                        - Key points you've extracted from the transcript
                        - Any challenges you encountered in the analysis, including inconsistencies or unclear parts in the transcript
                        
                        Your final output should be structured as follows:
                        
                        <output>
                        Speakers:
                        1. [Speaker Name]
                           - Biography: [Short biography]
                        2. [Speaker Name]
                           - Biography: [Short biography]
                        (Continue for all identified speakers)
                        
                        Summary:
                        [Your summary of the video content]
                        
                        Key Learnings:
                        [key insights and learnings. Give supporting detail for each key insight and learning.]
                        </output>
                        
                        Remember to only include speakers you can identify with high confidence, and ensure your summary captures the essence of the video content accurately.
                        """

#            summary = claude.query(system=system, message=message_summarize)
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

            datetime_stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"summaries/summary_{title}_{datetime_stamp}.txt"
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
