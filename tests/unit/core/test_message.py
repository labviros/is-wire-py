from __future__ import print_function
from is_wire.core import Message, now, ContentType, Status
from google.protobuf.struct_pb2 import Struct
import six
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


_integer = [int(-1)]
_string = [str("str")]
_float = [float(-1.0)]
_number = _integer + _float
_content_type = [ContentType.PROTOBUF]
_status = [Status()]
_dict = [{}]
no_check_FIX_ME = []


@pytest.mark.parametrize("property,valid_types,invalid_types",
                         [("topic", _string, _number),
                          ("reply_to", _string, _number),
                          ("subscription_id", _string, _number),
                          ("correlation_id", _integer, _float + _string),
                          ("content_type", _content_type, _number + _string),
                          ("created_at", no_check_FIX_ME, no_check_FIX_ME),
                          ("timeout", _number, _string),
                          ("status", _status, _number + _string),
                          ("metadata", _dict, _number + _string)])
def test_type_safety(property, valid_types, invalid_types):
    message = Message()
    for value in valid_types:
        print("valid value=", value)
        setattr(message, property, value)
        assert getattr(message, property) == value

    for value in invalid_types:
        print("invalid value=", value)
        with pytest.raises(TypeError):
            setattr(message, property, value)


def test_type_safety_body():
    message = Message()
    message.body = "string"
    assert message.body == str.encode("string")

    message.body = str.encode("string")
    assert message.body == str.encode("string")

    with pytest.raises(TypeError):
        message.body = -1

    with pytest.raises(TypeError):
        message.body = -1.0


@pytest.mark.parametrize("attr,value,checker", [
    ("topic", "string", Message.has_topic),
    ("reply_to", "string", Message.has_reply_to),
    ("subscription_id", "string", Message.has_subscription_id),
    ("correlation_id", -1, Message.has_correlation_id),
    ("body", "string", Message.has_body),
    ("content_type", ContentType.JSON, Message.has_content_type),
    ("timeout", 10.0, Message.has_timeout),
    ("status", Status(), Message.has_status),
])
def test_has_field(attr, value, checker):
    message = Message()
    assert checker(message) is False
    setattr(message, attr, value)
    assert checker(message) is True


def test_pack_unpack():
    struct = Struct()
    struct.fields["key"].number_value = 0.1212121921839893438974837

    message = Message()
    message.pack(struct)

    assert message.content_type == ContentType.PROTOBUF
    assert str(struct) == str(message.unpack(Struct))
    assert struct == message.unpack(Struct)

    message.content_type = ContentType.JSON
    message.pack(struct)
    assert str(struct) == str(message.unpack(Struct))
    assert struct == message.unpack(Struct)


def test_create_reply():
    request = Message()
    request.topic = "topic"
    request.reply_to = "reply_to"
    request.content_type = ContentType.JSON

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
