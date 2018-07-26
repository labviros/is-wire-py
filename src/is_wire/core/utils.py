import os
import uuid
from datetime import datetime


def new_uuid():
    return uuid.uuid4().int >> 64


def consumer_id():
    return '{}/{:X}'.format(os.uname()[1], new_uuid())


def now():
    return (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()


def assert_type(instance, types, name):

    if isinstance(types, list):
        types = tuple(types)

    if not isinstance(instance, types):
        if isinstance(types, tuple):
            types = " or ".join([t.__name__ for t in types])
            error = "Object {} must be of types {}".format(name, types)
        else:
            error = "Object {} must be of type {}".format(name, types.__name__)
        raise TypeError(error)
