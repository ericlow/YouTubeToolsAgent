from typing import List

import MainCli
from agents.youtube_agent import FilesystemAgentService
from MainCli import *
# what is the difference between an LLM and an agent?
"""
    what is it that separates an LLM, such as Claude or ChatGPT from an agent?  An agent has the ability to interact
    with the outside world.  It can do more than just chat with the user.  It does not have to work autonomously, but
    there certainly is that style of agent.
    does an agent have to have core business logic be the LLM? if your app is using LLM, but the core business logic is
    not driven by the LLM, is it still an agent? I think this is an app with AI, but not an agent.

"""
# what does this agent do?
"""
    the following agent will have the capability to interact with the filesystem and youtube.

    the responsibility of the agent is to create a file which contains a summary of videos watched.

    It will:
        be invoked by a watch(list of urls)
        check if a summary exists before retrieving the video
        create summaries of the videos and save to filesystem
        create a summary of the summaries and save to the filesystem
"""
# how does the Claude API work?
"""
    Questions about Claude API
        1. what is system? what's the difference between system and messages?
        2. what is temperature
        3. what are max tokens? how many tokens am I using?
        4. messages (that we send to claude) is an array
        5. what models exist? how do we find versions and when new ones are available?
        6. is interacting with the API completely different than interacting via the chat interface?
"""

if __name__ == '__main__':
    MainCli().cmdloop()

    fa = FilesystemAgentService(False)
#    fa.watch("https://www.youtube.com/watch?v=ZL14jkX39G0")
    # Benioff
    # Zuckerberg
    # Andressen Horowitz
    # Andrew Ng
    # jensen huang
    # Ycombinator
    # satya nadella
    url = "https://www.youtube.com/watch?v=TDPqt7ONUCY" #
    # url = "https://www.youtube.com/watch?v=-9rfzn-e-fY" # creatine
#    url = "https://www.youtube.com/watch?v=dsfOV6TYLzk" # soccer
    url ="https://www.youtube.com/watch?v=GPIuPRqDGG8" # how I got good at leetcode
    url = "https://www.youtube.com/watch?v=dzxiPOkbtR4"
    url = "https://www.youtube.com/watch?v=bI889qvShvk&t=3s" # what happened to milwaukee's impact driver
    # url = "https://www.youtube.com/watch?v=HF2rRxJvHUU" # Unc and Ocho react to Super Bowl LIX\
    # url = "https://www.youtube.com/watch?v=3TU0TzA08NE&t=1s"
    # url = "https://www.youtube.com/watch?v=0alFHX45pU4"
    # url = "https://www.youtube.com/watch?v=McZ7YOSmBAI" # health care affordability advisory meeting
    # url = "https://www.youtube.com/watch?v=bEKufM_im88" # kylie jenner
    url = "https://www.youtube.com/watch?v=rF9wmYHtJKc"
    fa.watch(url)

    short_list_urls = """
    https://www.youtube.com/watch?v=TDPqt7ONUCY,
    https://www.youtube.com/watch?v=sal78ACtGTc,
    https://www.youtube.com/watch?v=pBBe1pk8hf4,
    https://www.youtube.com/watch?v=VDmU0jjklBo&t=8s"""
#    fa.watch(short_list_urls)

    urls = """
    https://www.youtube.com/watch?v=TDPqt7ONUCY,
    https://www.youtube.com/watch?v=sal78ACtGTc,
    https://www.youtube.com/watch?v=pBBe1pk8hf4,
    https://www.youtube.com/watch?v=VDmU0jjklBo&t=8s,
    https://www.youtube.com/watch?v=z0wt2pe_LZM,
    https://www.youtube.com/watch?v=ASABxNenD_U&t=1s,
    https://www.youtube.com/watch?v=eBVi_sLaYsc&t=2s,
    https://www.youtube.com/watch?v=GuqAUv4UKXo,
    https://www.youtube.com/watch?v=kOkDTvsUuWA,
    https://www.youtube.com/watch?v=9NtsnzRFJ_o&t=1687s,
    https://www.youtube.com/watch?v=kfe3ajUYSdc,
    https://www.youtube.com/watch?v=k82RwXqZHY8,
    https://www.youtube.com/watch?v=KrRD7r7y7NY&t=56s,
    https://www.youtube.com/watch?v=9mylj0ogCFY,
    https://www.youtube.com/watch?v=B3ZaTU0Zn4M,
    https://www.youtube.com/watch?v=6twxFu3bL0w&t=289s,
    https://www.youtube.com/watch?v=OPRJI8Djfq8,
    https://www.youtube.com/watch?v=O6DtzLGLNWY&t=8s,
    https://www.youtube.com/watch?v=Vy3OkbtUa5k&t=53s,
    https://www.youtube.com/watch?v=2YN2-oEBCJw,
    https://www.youtube.com/watch?v=kfe3ajUYSdc&t=13"""
#    fa.watch(urls)



