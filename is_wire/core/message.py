import uuid
import json
from pika import BasicProperties

from .utils import current_time
from .subscription import Subscription

class Message:
    def __init__(self):
        self.__topic = None
        self.__sid = None
        self.__body = None
        self.__reply_to = None
        self.__correlation_id = None
        self.__content_type = None
        self.__created_at = current_time()
        self.__metadata = {}
        self.__on_reply = None
        self.__on_timeout = None
        self.__timeout_ms = None
        self.__ctag = None

    def get_properties(self):
        return BasicProperties(
            content_type=self.content_type(),
            timestamp=self.created_at(),
            headers=self.metadata(),
            reply_to=self.reply_to(),
            correlation_id=self.correlation_id(),
            expiration=self.timeout_ms()
        )

    def set_properties(self, props):
        self.set_created_at(props.timestamp)
        self.set_correlation_id(props.correlation_id)
        self.set_reply_to(props.reply_to)
        self.set_timeout_ms(props.expiration)
        self.set_content_type(props.content_type)
        headers = props.headers
        if 'rpc-status' in headers:
            rpc_status = headers['rpc-status']
            if isinstance(rpc_status, str):
                headers['rpc-status'] = json.loads(rpc_status)
        self.add_metadata(headers)

    def create_reply(self):
        rep_msg = Message()
        rep_msg.set_topic(self.reply_to())                 \
                .set_correlation_id(self.correlation_id()) \
                .set_content_type(self.content_type())
        return rep_msg

    def topic(self):
        return self.__topic
    
    def set_topic(self, topic):
        self.__topic = topic
        return self

    def reply_to(self):
        return self.__reply_to

    def set_reply_to(self, subscription):
        if isinstance(subscription, Subscription):
            self.__reply_to = subscription.name()
            self.__ctag = subscription.id()
            if self.__correlation_id == None:
                self.set_correlation_id(str(uuid.uuid1().int >> 64))
        elif isinstance(subscription, str):
            self.__reply_to = subscription
        return self

    def has_reply_to(self):
        return self.__reply_to != None

    def consumer_tag(self):
        return self.__ctag
    
    def set_consumer_tag(self, ctag):
        self.__ctag = ctag
        return self

    def has_consumer_tag(self):
        return self.__ctag != None

    def correlation_id(self):
        return self.__correlation_id

    def set_correlation_id(self, cid):
        self.__correlation_id = cid
        return self

    def has_correlation_id(self):
        return self.__correlation_id != None
    
    def body(self):
        return self.__body

    def set_body(self, body):
        self.__body = body
        return self

    def content_type(self):
        return self.__content_type
    
    def set_content_type(self, content_type):
        self.__content_type = content_type
        return self

    def set_created_at(self, created_at):
        self.__created_at = created_at
        return self

    def created_at(self):
        return self.__created_at

    def metadata(self):
        return self.__metadata

    def add_metadata(self, mdata):
        self.__metadata.update(mdata)
        return self

    def set_on_reply(self, handle):
        self.__on_reply = handle
        return self

    def on_reply(self):
        return self.__on_reply

    def has_on_reply(self):
        return self.__on_reply != None

    def set_on_timeout(self, handle):
        self.__on_timeout = handle
        return self

    def on_timeout(self):
        return self.__on_timeout

    def has_on_timeout(self):
        return self.__on_timeout != None

    def set_timeout_ms(self, ms):
        if ms != None:
            self.__timeout_ms = str(ms)
        return self
    
    def timeout_ms(self):
        return self.__timeout_ms
    
    def has_timeout_ms(self):
        return self.__timeout_ms != None

    def pack(self, obj):
        self.__body = obj.SerializeToString() if obj != None else ''
        self.__content_type = 'application/x-protobuf'
        return self

    def unpack(self, pb):
        msg = pb()
        msg.ParseFromString(self.__body)
        return msg
