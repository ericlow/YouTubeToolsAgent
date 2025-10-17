#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()

import cmd
from components.agents.chat_agent import ChatAgent
from components.services.chat_appllcation import ChatApplication
from logger_config import setup_logging, getLogger


class MainChat(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.logging = getLogger(__name__)
        self.prompt = ">  "
        self.app = ChatApplication()
        self.agent = ChatAgent()

    def default(self, line:str):
        if line.strip():
            response = self.agent.chat(
                line
            )
        self.logging.info(response)

    def do_exit(self, line:str):
        return True

if __name__ == '__main__':
    setup_logging()
    MainChat().cmdloop()