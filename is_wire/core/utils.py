import os
import uuid
from datetime import datetime

def current_time():
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)

def consumer_id():
    return '{}/{:X}'.format(os.uname()[1], uuid.uuid4().int >> 64)