import os
import uuid
from datetime import datetime


def current_time():
    return int(
        (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)


def assert_type(instance, types, name):
    if not isinstance(instance, types):
        if type(types) is tuple:
            types = " or ".join([t.__name__ for t in types])
            error = "Object {} must be of types {}".format(name, types)
        else:
            error = "Object {} must be of type {}".format(name, types.__name__)
        raise TypeError(error)


def new_uuid():
    return uuid.uuid1().int >> 64


def consumer_id():
    return '{}/{:X}'.format(os.uname()[1], new_uuid())
