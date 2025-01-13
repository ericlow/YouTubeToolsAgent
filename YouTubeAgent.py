
"""
    what is it that separates an LLM, such as Claude or ChatGPT from an agent?  An agent has the ability to interact
    with the outside world.  It can do more than just chat with the user.  It does not have to work autonomously, but
    there certainly is that style of agent.
    does an agent have to have core business logic be the LLM? if your app is using LLM, but the core business logic is
    not driven by the LLM, is it still an agent? I think this is an app with AI, but not an agent.

    the following agent will have the capability to interact with the filesystem and youtube.

    the responsibility of the agent is to create a file which contains a summary of videos watched.

    It will:
        be invoked by a watch(list of urls)
        check if a summary exists before retrieving the video
        create summaries of the videos and save to filesystem
        create a summary of the summaries and save to the filesystem

    Questions about Claude API
        1. what is system? what's the difference between system and messages?
        2. what is temperature
        3. what are max tokens? how many tokens am I using?
        4. messages (that we send to claude) is an array
        5. what models exist? how do we find versions and when new ones are available?
        6. is interacting with the API completely different than interacting via the chat interface?


"""
from youtube import YouTubeService
from anthropicapp import Claude
class FilesystemAgentService:
    def __init__(self, mock:bool):
        self.mock = mock
    def watch(self, urls: str):
        """

        :param urls: list of urls to watch
        :return: {
                    count : number of videos watched
                    summaries : [
                                    {
                                        filename: "location",
                                        title: the video title,
                                        short: a 20 word summary of content
                                    },
                                    ...
                                    {
                                        filename: "location",
                                        title: the video title,
                                        short: a 20 word summary of content
                                    },
                                ],
                    summary : {
                                filename : "location"
                                short : a 20 word summary of content
                                }

                    }
        """
        if urls is None or len(urls) == 0:
            youtube = YouTubeService(self.mock)
            claude = Claude(self.mock)
            print(youtube.mock)
            list = urls.split(",")
            for url in list:
                transcript = youtube.get_transcript(url)
                summary = claude.summarize_transcript(transcript)
                print(summary)
        else:
            # do we need a claude session? is claude api stateless?
            # claude should get a list of 10 videos worth watching via youtube search
            # claude should watch, then summarize all the videos
            # claude should decide what videos are worth summarizing
            # claude should create a summary of important videos
            pass
