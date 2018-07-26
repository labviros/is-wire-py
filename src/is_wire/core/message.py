from subscription import Subscription
from is_msgs.wire_pb2 import ContentType
from datetime import datetime
from utils import now, assert_type, new_uuid


class Message(object):
    def __init__(self, obj=None):
        self._topic = None
        self._body = ''
        self._reply_to = None
        self._subscription_id = None
        self._correlation_id = None
        self._content_type = None
        self._created_at = now()
        self._metadata = {}
        self._timeout = None

        if obj != None:
            self.pack(obj)

    def __str__(self):
        pretty = "Message {\n"
        pretty += "  topic = {}\n".format(self.topic)
        created_at = datetime.fromtimestamp(self.created_at)
        pretty += "  created_at = {}\n".format(created_at)
        if self.has_correlation_id():
            pretty += "  correlation_id = {}\n".format(self.correlation_id)
        if self.has_reply_to():
            pretty += "  reply_to = {}\n".format(self.reply_to)
        if self.has_subscription_id():
            pretty += "  subscription_id = {}\n".format(self.subscription_id)
        if self.has_timeout():
            pretty += "  timeout = {}\n".format(self.timeout)
        if self.has_metadata():
            pretty += "  metadata = {}\n".format(self.metadata)
        if self.has_content_type():
            pretty += "  content_type = {}\n".format(
                ContentType.Name(self.content_type))
        pretty += "  body[{}] = {} \n".format(len(self.body), repr(self.body))
        pretty += "}\n"
        return pretty

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def create_reply(self):
        reply = Message()
        if self.has_reply_to():
            reply.topic = self.reply_to
        if self.has_correlation_id():
            reply.correlation_id = self.correlation_id
        if self.has_content_type():
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

    def has_topic(self):
        return self._topic != None and len(self._topic) != 0

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
            self._reply_to = value.name
            self.subscription_id = value.id

        elif isinstance(value, str):
            self._reply_to = value

    def has_reply_to(self):
        return self._reply_to != None and len(self._reply_to) != 0

    ## subscription_id

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        assert_type(value, str, "subscription_id")
        self._subscription_id = value

    def has_subscription_id(self):
        return self._subscription_id != None and len(
            self._subscription_id) != 0

    ## correlation_id

    @property
    def correlation_id(self):
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value):
        assert_type(value, (int, long), "correlation_id")
        self._correlation_id = value

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

    def has_body(self):
        return self._body != None and len(self._body) != 0

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

    def has_created_at(self):
        return self._created_at != None

    ## metadata

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        assert_type(value, dict, "metadata")
        self._metadata = value

    def has_metadata(self):
        return len(self._metadata) != 0

    ## on_reply

    @property
    def on_reply(self):
        return self._on_reply

    @on_reply.setter
    def on_reply(self, handle):
        #assert_type(handle, (), "on_reply")
        self._on_reply = handle

    def has_on_reply(self):
        return self._on_reply != None

    ## timeout

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, seconds):
        assert_type(seconds, (int, float, long), "timeout")
        self._timeout = seconds

    def has_timeout(self):
        return self._timeout != None

    ##

    def pack(self, obj):
        if not self.has_content_type():
            self.content_type = "protobuf"

        if self.content_type == ContentType.Value("PROTOBUF"):
            self.body = obj.SerializeToString()
        else:
            raise NotImplementedError(
                "Serialization to '{}' type not implemented".format(
                    ContentType.Name(self.content_type)))

    def unpack(self, schema):
        obj = schema()
        if not self.has_content_type():
            self.content_type = "protobuf"

        if self.content_type == ContentType.Value("PROTOBUF"):
            obj.ParseFromString(self.body)
        else:
            raise NotImplementedError(
                "Deserialization from '{}' type not implemented".format(
                    ContentType.Name(self.content_type)))

        return obj
