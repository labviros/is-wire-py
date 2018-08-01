from datetime import datetime
from google.protobuf import json_format
from six import integer_types, string_types, binary_type

from .utils import now, assert_type, new_uuid
from .subscription import Subscription
from .wire.status import Status
from .wire.content_type import ContentType
from .tracing.propagation import TextFormatPropagator


class Message(object):
    def __init__(self, content=None, reply_to=None, content_type=None):
        """ Creates a new message.
        Args:
            content (str or object): sets the message body with the
            given content. If an object is provided, it will be packed
            using the given content_type.

            content_type (ContentType): describes how the content will
            be serialized.

            reply_to (str or Subscription): indicates where the reply to
            this message should be sent to.
        """
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
            if isinstance(content, binary_type):
                self.body = content
            else:
                self.pack(content)

    def __str__(self):
        """ Converts a message to a verbose string of its properties """
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
        pretty += "}"
        return pretty

    def short_string(self):
        """ Converts a message to a simplified string of its properties, empty
         fields are not printed """
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
        """ Returns True if the messages are equal, False otherwise """
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
        """ str: Topic where the message was published or is going
         to be published """
        return self._topic

    @topic.setter
    def topic(self, topic):
        assert_type(topic, string_types, "topic")
        self._topic = topic

    def has_topic(self):
        """ Returns: True if the property topic of the message is set,
         False otherwise """
        return bool(self._topic)

    # reply_to

    @property
    def reply_to(self):
        """ str: Topic where the reply to this message should be published.
         When setting this property an object of type Subscription can be
         passed to automatically set this value. The correlation_id field
         is automatically set if empty. """
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
        """ Returns: True if the property reply_to of the message is set,
         False otherwise """
        return bool(self._reply_to)

    # subscription_id

    @property
    def subscription_id(self):
        """ str: ID of the subscription that this message belongs to """
        return self._subscription_id

    @subscription_id.setter
    def subscription_id(self, value):
        assert_type(value, string_types, "subscription_id")
        self._subscription_id = value

    def has_subscription_id(self):
        """ Returns: True if the property subscription_id of the message is set,
         False otherwise """
        return bool(self._subscription_id)

    # correlation_id

    @property
    def correlation_id(self):
        """ int: Unique ID used to correlate reply/response messages """
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value):
        assert_type(value, integer_types, "correlation_id")
        self._correlation_id = value

    def has_correlation_id(self):
        """ Returns: True if the property correlation_id of the message is set,
         False otherwise """
        return self._correlation_id is not None

    # body

    @property
    def body(self):
        """ bytes: Raw content of the message """
        return self._body

    @body.setter
    def body(self, value):
        assert_type(value, binary_type, "body")
        self._body = value

    def has_body(self):
        """ Returns: True if the property body of the message is set,
         False otherwise """
        return bool(self._body)

    # content_type

    @property
    def content_type(self):
        """ ContentType: Indicates how the content/body of the message
        was serialized """
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        assert_type(value, ContentType, "content_type")
        self._content_type = value

    def has_content_type(self):
        """ Returns: True if the property content_type of the message is set,
         False otherwise """
        return self._content_type is not None

    # created_at

    @property
    def created_at(self):
        """ float: Seconds since the epoch indicating when the message
        was created"""
        return self._created_at

    @created_at.setter
    def created_at(self, timestamp):
        # assert_type(timestamp, (), "created_at")
        self._created_at = timestamp

    def has_created_at(self):
        """ Returns: True if the property created_at of the message is set,
         False otherwise """
        return self._created_at is not None

    # metadata

    @property
    def metadata(self):
        """ dict: Key-value pairs which any can model any type of extra
        information about the message """
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        assert_type(value, dict, "metadata")
        self._metadata = value

    def has_metadata(self):
        """ Returns: True if the property metadata of the message is set,
         False otherwise """
        return len(self._metadata) != 0

    # timeout

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, seconds):
        assert_type(seconds, [float] + list(integer_types), "timeout")
        self._timeout = seconds

    def has_timeout(self):
        """ Returns: True if the property timeout of the message is set,
         False otherwise """
        return self._timeout is not None

    def deadline_exceeded(self):
        if not self.has_timeout():
            return False
        return now() > self.created_at + self.timeout

    # status

    @property
    def status(self):
        """ Status representing the success or not of a RPC """
        return self._status

    @status.setter
    def status(self, value):
        assert_type(value, Status, "status")
        self._status = value

    def has_status(self):
        """ Returns: True if the property status of the message is set,
         False otherwise """
        return self._status is not None

    # tracing

    def extract_tracing(self):
        return TextFormatPropagator.from_carrier(self.metadata)

    def inject_tracing(self, span):
        span_context = TextFormatPropagator.new_span_context(
            trace_id=span.context_tracer.trace_id,
            span_id=span.span_id,
        )
        self.metadata = TextFormatPropagator.to_carrier(
            span_context, self.metadata)

    # pack / unpack

    def pack(self, obj):
        """ Serializes the given object using the specified message
        content_type. If the message has no content_type, the protobuf
        format is used.
        Args:
            obj (object): protobuf object to be serialized.
        """
        if not self.has_content_type():
            self.content_type = ContentType.PROTOBUF

        if self.content_type == ContentType.PROTOBUF:
            # SerializeToString returns py2: str, py3: bytes
            self.body = obj.SerializeToString()

        elif self.content_type == ContentType.JSON:
            # MessageToJson returns py2: str, py3: str
            packed = json_format.MessageToJson(
                obj, indent=0, including_default_value_fields=True)
            if not isinstance(packed, binary_type):
                self.body = packed.encode('latin')
            else:
                self.body = packed
        else:
            raise NotImplementedError(
                "Serialization to '{}' type not implemented".format(
                    self.content_type.name))

    def unpack(self, schema):
        """ Deserializes the content of the message using the given schema.
        If the message has no content_type, the protobuf format is used.
        Args:
            schema (type): type of the protobuf object to be deserialized.
        Returns:
            schema: deserialized instance of the object of type schema.
        """
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
