from datetime import datetime
from google.protobuf import json_format
from six import integer_types, string_types, binary_type
import six

from .utils import now, assert_type, new_uuid
from .subscription import Subscription
from .wire.status import Status
from .wire.content_type import ContentType
from .tracing.propagation import TextFormatPropagator


class Message(object):
    def __init__(self, content=None, reply_to=None, content_type=None):
        self._topic = None
        self._body = ''
        self._reply_to = None
        self._subscription_id = None
        self._correlation_id = None
        self._content_type = None
        self._created_at = now()
        self._metadata = {}
        self._timeout = None
        self._status = None

        if reply_to is not None:
            self.reply_to = reply_to

        if content_type is not None:
            self.content_type = content_type

        if content is not None:
            if isinstance(content, six.string_types):
                self.content = content
            else:
                self.pack(content)

    def __str__(self):
        created_at = datetime.fromtimestamp(self.created_at)
        pretty = "{\n"
        pretty += "  topic = '{}'\n".format(self.topic or "")
        pretty += "  created_at = {}\n".format(created_at)
        pretty += "  correlation_id = {}\n".format(self.correlation_id)
        pretty += "  reply_to = '{}'\n".format(self.reply_to or "")
        pretty += "  subscription_id = '{}'\n".format(self.subscription_id
                                                      or "")
        pretty += "  timeout = {}\n".format(self.timeout)
        pretty += "  status = {}\n".format(self.status)
        pretty += "  metadata = {}\n".format(self.metadata)
        pretty += "  content_type = {}\n".format(self.content_type)
        pretty += "  body[{}] = {} \n".format(len(self.body), repr(self.body))
        pretty += '}\"'
        return pretty

    def short_string(self):
        created_at = datetime.fromtimestamp(self.created_at)
        pretty = "{"
        pretty += "topic='{}'".format(self.topic)
        pretty += " created_at={}".format(created_at)
        if self.has_correlation_id():
            pretty += " correlation_id={}".format(self.correlation_id)
        if self.has_reply_to():
            pretty += " reply_to='{}'".format(self.reply_to)
        if self.has_subscription_id():
            pretty += " subscription_id='{}'".format(self.subscription_id)
        if self.has_timeout():
            pretty += " timeout={}".format(self.timeout)
        if self.has_status():
            pretty += " status={}".format(self.status)
        if self.has_metadata():
            pretty += " metadata={}".format(self.metadata)
        if self.has_content_type():
            pretty += " content_type={}".format(self.content_type)
        pretty += " body[{}]={}".format(len(self.body), repr(self.body))
        pretty += "}"
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

    # topic

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, topic):
        assert_type(topic, string_types, "topic")
        self._topic = topic

    def has_topic(self):
        return self._topic is not None and len(self._topic) != 0

    # reply_to

    @property
    def reply_to(self):
        return self._reply_to

    @reply_to.setter
    def reply_to(self, value):
        assert_type(value, list(string_types) + [Subscription], "reply_to")

        if self.correlation_id is None:
            self.correlation_id = new_uuid()

        if isinstance(value, Subscription):
            self._reply_to = value.name
            self.subscription_id = value.id

        elif isinstance(value, string_types):
            self._reply_to = value

    def has_reply_to(self):
        return self._reply_to is not None and len(self._reply_to) != 0

    # subscription_id

    @property
    def subscription_id(self):
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        assert_type(value, string_types, "subscription_id")
        self._subscription_id = value

    def has_subscription_id(self):
        return self._subscription_id is not None and len(
            self._subscription_id) != 0

    # correlation_id

    @property
    def correlation_id(self):
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value):
        assert_type(value, integer_types, "correlation_id")
        self._correlation_id = value

    def has_correlation_id(self):
        return self._correlation_id is not None

    # body

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        assert_type(value, [binary_type] + list(string_types), "body")
        self._body = six.b(value) if isinstance(value, string_types) else value

    def has_body(self):
        return self._body is not None and len(self._body) != 0

    # content_type

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        assert_type(value, ContentType, "content_type")
        self._content_type = value

    def has_content_type(self):
        return self._content_type is not None

    # created_at

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, timestamp):
        # assert_type(timestamp, (), "created_at")
        self._created_at = timestamp

    def has_created_at(self):
        return self._created_at is not None

    # metadata

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        assert_type(value, dict, "metadata")
        self._metadata = value

    def has_metadata(self):
        return len(self._metadata) != 0

    # on_reply

    @property
    def on_reply(self):
        return self._on_reply

    @on_reply.setter
    def on_reply(self, handle):
        # assert_type(handle, (), "on_reply")
        self._on_reply = handle

    def has_on_reply(self):
        return self._on_reply is not None

    # timeout

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, seconds):
        assert_type(seconds, [float] + list(integer_types), "timeout")
        self._timeout = seconds

    def has_timeout(self):
        return self._timeout is not None

    def deadline_exceeded(self):
        if not self.has_timeout():
            return False
        return now() > self.created_at + self.timeout

    # status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        assert_type(value, Status, "status")
        self._status = value

    def has_status(self):
        return self._status is not None

    # tracing

    def extract_tracing(self):
        return TextFormatPropagator.from_carrier(self.metadata)

    def inject_tracing(self, span):
        span_context = TextFormatPropagator.new_span_context(
            trace_id=span.context_tracer.trace_id,
            span_id=span.span_id,
        )
        self.metadata = TextFormatPropagator.to_carrier(span_context,
                                                        self.metadata)

    # pack / unpack

    def pack(self, obj):
        if not self.has_content_type():
            self.content_type = ContentType.PROTOBUF

        if self.content_type == ContentType.PROTOBUF:
            self.body = obj.SerializeToString()
        elif self.content_type == ContentType.JSON:
            self.body = json_format.MessageToJson(
                obj, indent=0, including_default_value_fields=True)
        else:
            raise NotImplementedError(
                "Serialization to '{}' type not implemented".format(
                    self.content_type.name))

    def unpack(self, schema):
        obj = schema()
        if not self.has_content_type():
            self.content_type = ContentType.PROTOBUF

        if self.content_type == ContentType.PROTOBUF:
            obj.ParseFromString(self.body)
        elif self.content_type == ContentType.JSON:
            obj = json_format.Parse(self.body, obj)
        else:
            raise NotImplementedError(
                "Deserialization from '{}' type not implemented".format(
                    self.content_type.name))

        return obj
