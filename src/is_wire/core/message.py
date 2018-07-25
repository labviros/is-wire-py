import uuid
import json
from pika import BasicProperties

from .utils import current_time, assert_type, new_uuid
from .subscription import Subscription
from is_msgs.wire_pb2 import ContentType


class Message(object):
    def __init__(self, obj=None):
        self._topic = None
        self._body = ''
        self._reply_to = None
        self._subscription_id = None
        self._correlation_id = None
        self._content_type = None
        self._created_at = current_time()
        self._metadata = {}
        self._on_reply = None
        self._on_timeout = None
        self._timeout = None

        if obj != None:
            self.pack(obj)

    def to_amqp_properties(self):
        return BasicProperties(
            content_type=self.content_type,
            timestamp=self.created_at,
            headers=self.metadata,
            reply_to=self.reply_to,
            correlation_id=self.correlation_id,
            expiration=self.timeout_ms)

    def from_amqp_properties(self, props):
        self.created_at = props.timestamp
        self.correlation_id = props.correlation_id
        self.reply_to = props.reply_to
        self.timeout_ms = props.expiration
        self.content_type = props.content_type

        self.metadata = props.headers
        if 'rpc-status' in self.metadata:
            status = self.metadata['rpc-status']
            if isinstance(status, str):
                self.metadata['rpc-status'] = json.loads(status)

    def create_reply(self):
        reply = Message()
        reply.topic = self.reply_to
        reply.correlation_id = self.correlation_id
        reply.content_type = self.content_type
        return reply

    ## topic

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, topic):
        assert_type(topic, str, "topic")
        self._topic = topic
        return self

    ## reply_to

    @property
    def reply_to(self):
        return self._reply_to

    @reply_to.setter
    def reply_to(self, value):
        assert_type(value, (str, Subscription), "reply_to")

        if self.correlation_id == None:
            self.correlation_id = new_uuid()

        if isinstance(value, Subscription):
            self._reply_to = value.name()
            self.subscription_id = value.id()

        elif isinstance(value, str):
            self._reply_to = value

        return self

    def has_reply_to(self):
        return self._reply_to != None

    ## subscription_id

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        assert_type(value, str, "subscription_id")
        self._subscription_id = value
        return self

    def has_subscription_id(self):
        return self.subscription_id != None

    ## correlation_id

    @property
    def correlation_id(self):
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value):
        assert_type(value, (int, long), "correlation_id")
        self._correlation_id = value
        return self

    def has_correlation_id(self):
        return self._correlation_id != None

    ## body

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        assert_type(value, (bytes, str), "body")
        self._body = value
        return self

    def has_body(self):
        return self._body != None and self._body != ""

    ## content_type

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        assert_type(value, (str, int), "content_type")

        if isinstance(value, str):
            self._content_type = ContentType.Value(value.upper())
        elif isinstance(value, int):
            self._content_type = value

        return self

    def has_content_type(self):
        return self._content_type != None

    ## created_at

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, timestamp):
        #assert_type(timestamp, (), "created_at")
        self._created_at = timestamp
        return self

    ## metadata

    @property
    def metadata(self):
        return self._metadata

    ## on_reply

    @property
    def on_reply(self):
        return self._on_reply

    @on_reply.setter
    def on_reply(self, handle):
        #assert_type(handle, (), "on_reply")
        self._on_reply = handle
        return self

    def has_on_reply(self):
        return self._on_reply != None

    ## on_timeout

    @property
    def on_timeout(self):
        return self._on_timeout

    @on_timeout.setter
    def on_timeout(self, handle):
        #assert_type(handle, (), "on_timeout")
        self._on_timeout = handle
        return self

    def has_on_timeout(self):
        return self._on_timeout != None

    ##

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, milliseconds):
        assert_type(milliseconds, (int, float, long), "timeout")
        self._timeout = milliseconds
        return self

    def has_timeout(self):
        return self._timeout != None

    ##

    @staticmethod
    def content_type_to_wire(content_type):
        """ Converts an object of type ContentType to the wire string representation 
        Args:
            content_type (ContentType): enum value
        Returns:
            str: wire string representation
        """
        if content_type == ContentType.Value("PROTOBUF"):
            return 'application/x-protobuf'

    def pack(self, obj):
        if not self.has_content_type():
            self.content_type = "protobuf"

        if self.content_type == ContentType.Value("PROTOBUF"):
            self.body = obj.SerializeToString()
        else:
            raise NotImplementedError(
                "Serialization to '{}' type not implemented".format(
                    ContentType.Name(self.content_type)))

        return self

    def unpack(self, schema):
        obj = schema()
        if not self.has_content_type():
            self.content_type = "protobuf"

        if self.content_type == ContentType.Value("PROTOBUF"):
            self.body = obj.SerializeToString()
            obj.ParseFromString(self.body)
        else:
            raise NotImplementedError(
                "Deserialization from '{}' type not implemented".format(
                    ContentType.Name(self.content_type)))

        return obj
