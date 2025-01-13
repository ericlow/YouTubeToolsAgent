from YouTubeAgent import FilesystemAgentService


def print_hi(name):
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    fa = FilesystemAgentService(True)
    fa.watch("youtube/1, youtube/2")