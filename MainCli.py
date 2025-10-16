#!/usr/bin/env python3
import cmd
from dotenv import load_dotenv
from components.cli_application import CliApplication

class MainCli(cmd.Cmd):
    prompt = "> "
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.app = CliApplication()

    def do_test(self, arg):
        self.app.do_test()

    def do_e(self, arg):
        self.do_exit(arg)

    def do_exit(self, arg):
        """exit the app"""
        print("Goodbye")
        return True

    def do_lv(self, arg):
        self.do_list_videos(arg)

    def do_list_videos(self, arg):
        print(f"list all videos")
        output = self.app.list_all_videos()
        print(output)

    def do_sv(self, id):
        self.do_summarize_video(id)

    def do_summarize_video(self, id):
        if len(id) == 0:
            self.app.summarize_video(-1)
        else:
            print(f"summarize video: {id}")
            self.app.summarize_video(int(id))

    def do_wv(self, url):
        self.do_watch_video(url)

    def do_watch_video(self, url):
        print(f"get watch video: {url}")
        self.app.watch_video(url)

    def do_save_transcript(self, arg):
        id, filename = arg.split(maxsplit=1)
        print(f"save video to file: {filename}")
        self.app.save_transcript(int(id), filename)

    def do_q(self, arg):
        self.do_ask_question(arg)

    def do_ask_question(self, arg):
        self.app.ask_question(id, arg)

if __name__ == '__main__':
    MainCli().cmdloop()
