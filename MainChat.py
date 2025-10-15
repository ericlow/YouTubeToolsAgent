#!/usr/bin/env python3
import cmd
from dotenv import load_dotenv

from chat_agent import ChatAgent
from chat_appllcation import ChatApplication
from components.tool_executor import ToolExecutor

class MainChat(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = ">  "
        load_dotenv()
        self.app = ChatApplication()
        self.agent = ChatAgent()

    def default(self, line:str):
        if line.strip():
            response = self.agent.chat(
                line
            )
            print(f"agent: {response}")

    def do_exit(self, line:str):
        return True

if __name__ == '__main__':
    MainChat().cmdloop()