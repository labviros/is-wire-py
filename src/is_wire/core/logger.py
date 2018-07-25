import sys
import logging
from uuid import uuid4
from datetime import datetime
from termcolor import colored

from .utils import current_time

''' based on: https://gist.github.com/brainsik/1238935 '''
class ColorLog(object):

    colormap = dict(
        info=dict(color='white'),
        warn=dict(color='yellow'),
        error=dict(color='red'),
        critical=dict(color='white', on_color='on_red', attrs=['bold']),
    )

    def __init__(self, logger):
        self._log = logger

    def __getattr__(self, name):
        if name in ['info', 'warn', 'error', 'critical']:
            return lambda s, *args: getattr(self._log, name)(
                colored(s, **self.colormap[name]), *args)

        return getattr(self._log, name)

''' based on: https://stackoverflow.com/questions/6290739/python-logging-use-milliseconds-in-time-format'''
class MyFormatter(logging.Formatter):
    converter = datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime('%d-%m-%Y %H:%M:%S')
            s = '%s:%03d' % (t, record.msecs)
        return s

class Logger:
    def __init__(self, name='__name__', level=logging.INFO):
        self.LOGGING_FMT = '[%(levelname)s][%(process)d][%(asctime)s] %(message)s'
        self.log = ColorLog(logging.getLogger(name='{}{:X}'.format(name, uuid4().int >> 64)))
        formatter = MyFormatter(fmt=self.LOGGING_FMT)
        console = logging.StreamHandler()
        self.log.addHandler(console)
        console.setFormatter(formatter)
        self.log.setLevel(level)

    def info(self, formatter, *args):
        self.log.info(formatter.format(*args))

    def warn(self, formatter, *args):
        self.log.warn(formatter.format(*args))

    def error(self, formatter, *args):
        self.log.error(formatter.format(*args))
    
    def critical(self, formatter, *args):
        self.log.critical(formatter.format(*args))
        sys.exit(-1)