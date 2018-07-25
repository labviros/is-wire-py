from is_wire.core import Message
from is_msgs.wire_pb2 import ContentType
import pytest


def test_default_constructor():
    message = Message()
    assert message.has_body() is False
    assert message.has_content_type() is False
    assert message.has_correlation_id() is False
    assert message.has_on_reply() is False
    assert message.has_on_timeout() is False
    assert message.has_reply_to() is False
    assert message.has_subscription_id() is False
    assert message.has_timeout() is False


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

@pytest.mark.parametrize("property,valid_types", [
    ("topic", string_only),
    ("reply_to", string_only),
    ("subscription_id", string_only),
    ("correlation_id", integer_only),
    ("body", string_only),
    #("content_type", content_type_only),
    ("created_at", no_check_FIX_ME),
    ("on_reply", no_check_FIX_ME),
    ("on_timeout", no_check_FIX_ME),
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
