import os

import colorlog
import logging

def create_file_handler():
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    return file_handler


class WhiteListFilter(logging.Filter):
    def __init__(self, whitelist: list[str]):
        super().__init__()
        self.whitelist = whitelist

    def filter(self, record):
        for pattern in self.whitelist:
            if record.name == pattern or record.name.startswith(pattern + '.'):
                return True
        return False

def create_console_handler():
    whitelist = ['api','domain','infrastructure','components', '__main__']

    console_handler = colorlog.StreamHandler()
    console_handler.addFilter(WhiteListFilter(whitelist))
    console_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s %(levelname)s - %(message)s',
        log_colors={
            'DEBUG':'light_black',
            'INFO':'green',
            'WARNING': 'yellow',
            'ERROR':'red'
        }
    ))
    return console_handler



def setup_logging():

    # setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(create_console_handler())
    logger.addHandler(create_file_handler())

def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(level=getLogLevel())
    return logger

def getLogLevel():
    log_level_str = os.getenv("LOG_LEVEL")
    LOG_LEVEL = getattr(logging, log_level_str.upper())
    return LOG_LEVEL