from is_wire.core import Message, now
from is_msgs.wire_pb2 import ContentType
from is_msgs.wire_pb2 import WireFormat
import pytest


def test_default_constructor():
    message = Message()
    assert message.has_body() is False
    assert message.has_topic() is False
    assert message.has_created_at() is True
    assert message.has_content_type() is False
    assert message.has_correlation_id() is False
    assert message.has_reply_to() is False
    assert message.has_subscription_id() is False
    assert message.has_timeout() is False
    assert message.has_metadata() is False


string_only = [
    ("string", True),
    (int(-1), False),
    (long(-1), False),
    (0.0, False),
]

integer_only = [
    ("string", False),
    (int(-1), True),
    (long(-1), True),
    (0.0, False),
]

number_only = [
    ("string", False),
    (int(-1), True),
    (long(-1), True),
    (0.0, True),
]

no_check_FIX_ME = []


@pytest.mark.parametrize(
    "property,valid_types",
    [
        ("topic", string_only),
        ("reply_to", string_only),
        ("subscription_id", string_only),
        ("correlation_id", integer_only),
        ("body", string_only),
        #("content_type", content_type_only),
        ("created_at", no_check_FIX_ME),
        ("timeout", number_only),
    ])
def test_type_safety(property, valid_types):
    message = Message()
    for value, should_work in valid_types:
        if should_work:
            setattr(message, property, value)
            assert getattr(message, property) is value
        else:
            with pytest.raises(TypeError):
                setattr(message, property, value)


@pytest.mark.parametrize("attr,value,checker", [
    ("topic", "string", Message.has_topic),
    ("reply_to", "string", Message.has_reply_to),
    ("subscription_id", "string", Message.has_subscription_id),
    ("correlation_id", -1, Message.has_correlation_id),
    ("body", "string", Message.has_body),
    ("content_type", "json", Message.has_content_type),
    ("timeout", 10.0, Message.has_timeout),
])
def test_has_field(attr, value, checker):
    message = Message()
    assert checker(message) is False
    setattr(message, attr, value)
    assert checker(message) is True


def test_pack_unpack():
    wire = WireFormat()
    wire.raw = "body body"

    message = Message()
    message.pack(wire)
    print repr(message.body)
    assert str(wire) == str(message.unpack(WireFormat))

    message.content_type = "json"


def test_create_reply():
    request = Message()
    request.topic = "topic"
    request.reply_to = "reply_to"
    request.content_type = "json"

    reply = request.create_reply()

    assert reply.topic == request.reply_to
    assert reply.correlation_id == request.correlation_id
    assert reply.content_type == request.content_type


def test_create_reply_empty_request():
    request = Message()
    request.topic = "topic"

    reply = request.create_reply()

    assert reply.topic == request.reply_to
    assert reply.correlation_id == request.correlation_id
    assert reply.content_type == request.content_type
