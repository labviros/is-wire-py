from colorlog import ColoredFormatter, StreamHandler, getLogger
from sys import exit
import logging
from .utils import assert_type


class Logger:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARN
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, name, level=logging.DEBUG):
        assert_type(name, str, "name")

        style = "%(log_color)s[%(levelname)-.1s][%(threadName)s]" \
                "[%(asctime)s][%(name)s] %(message)s"

        formatter = ColoredFormatter(
            style,
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'white,bg_red',
            },
            secondary_log_colors={},
            style='%')

        self.logger = getLogger(name)
        if len(self.logger.handlers) == 0 and name:
            handler = StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.set_level(level)

    def set_level(self, level):
        self.logger.setLevel(level)

    def debug(self, formatter, *args):
        self.logger.debug(formatter.format(*args))

    def info(self, formatter, *args):
        self.logger.info(formatter.format(*args))

    def warn(self, formatter, *args):
        self.logger.warning(formatter.format(*args))

    def error(self, formatter, *args):
        self.logger.error(formatter.format(*args))

    def critical(self, formatter, *args):
        self.logger.critical(formatter.format(*args))
        exit(-1)
