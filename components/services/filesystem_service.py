import os
import json
from json import JSONDecoder, JSONEncoder
from typing import List, Any


class FileSystemService:
    pass

    def get_filenames(self):
        filenames = []
        filenames.append("1")
        filenames.append("2")
        return filenames

    def execute(self, commands: list[str]) -> list[str]:
        for command in commands:
            action = command["action"]
            if action == "read":
                result = """
                    {
                        "code" = OK,
                        "files" = [
                            "a.txt",
                            "b.txt"
                        ]
                    }
                """
                command["result"] = result
            elif action == "rename":
                args = command["args"]
                source = args["source"]
                destination = args ["destination"]
                result = {}
                result["code"] = "OK"
                command["result"] = result

        return commands

if __name__ == '__main__':
    fs = FileSystemService()

    #    Read the transcript file
    file_path = "commands.json"

    commands = None
    with open(file_path, 'r', encoding='utf-8') as f:
        commandsT = f.read()
        d = JSONDecoder()
        commands = d.decode(commandsT)
    results = fs.execute(commands)

    with open(file_path+'.txt','w') as nf:
        e = JSONEncoder()
        r = e.encode(results)

        nf.write(r)
        nf.close()
