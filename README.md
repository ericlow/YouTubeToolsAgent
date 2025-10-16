# YouTubeToolsAgent
A chat agent for summarizing YouTube videos

# Setup
1. Create a virtual environment `python -m venv venv` the app was built in v3.11.5
1. Activate the virtual env 
     1. *nix: `source venv/bin/activate`
     2. Windows: `venv\Scripts\activate`
1. Install dependencies: `pip install -r requirements.txt`
1. create an `.env` file in the project root with the following content
```commandline
YOUTUBE_API_KEY=<YOUTUBE API KEY>
ANTHROPIC_API_KEY=<ANTHROPIC API KEY>
LOG_LEVEL=DEBUG
```
<!--
claude keys are available here: https://console.anthropic.com/settings/keys
youtube keys are available here: https://console.cloud.google.com/apis/credentials?pli=1&project=resfracweather
-->

# Application 2

## Start the app
activate the virtual env first
```
> ./MainChat.py
```

## Use the app

> \> I want you to watch two videos and tell me which one is better to learn about the current state of AI.  Here are the videos: https://www.youtube.com/watch?v=L32th5fXPw8 https://www.youtube.com/watch?v=obqjIoKaqdM&t=7s <br>
 \> ok that's not what I'm looking for.  Try this next one https://www.youtube.com/watch?v=DdlMoRSojtE https://www.youtube.com/watch?v=esqPTMDvw7w https://www.youtube.com/watch?v=264QcC094Vk


# Application 1 [Currently Broken]
The command line app is a command driven CLI. Users type explicit commands.

## Start the app
activate the virtual env first
```
> ./MainCli.py
```
## Use the app
````commandline
> help
> watch_video https://www.youtube.com/watch?v=obqjIoKaqdM
> list_videos
> summarize_video 0
> ask_question who is the creator, what channel is this?
````

## TODO 
* expose the prompts in a config file so they can more easily be edited
* select Claude model from a single config
* use the Claude stream interface to provide more frequent responses to the user, instead of all at once
* ChatSession is not symmetric.  ChatMessages are input, but anthropic messages are returned.