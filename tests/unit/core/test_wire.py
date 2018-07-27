from is_wire.core import Message, now, ContentType, StatusCode, Status
from is_wire.core.wire.conversion import WireV1
import six
import librabbitmq
import pytest


def test_amqp_conversion():
    message = Message()
    message.created_at = int(now() * 1000) / 1000.0
    message.reply_to = "reply_to"
    message.subscription_id = "subscription_id"
    message.content_type = ContentType.JSON
    message.body = '{"field":"value"}'
    message.topic = "MyTopic"
    message.status = Status(
        code=StatusCode.FAILED_PRECONDITION, why="Bad Args...")

    if isinstance(message.body, bytes):
        memory_view = memoryview(message.body)
    else:
        memory_view = memoryview(six.b(message.body))

    amqp = librabbitmq.Message(
        channel=None,
        properties=WireV1.to_amqp_properties(message),
        delivery_info={
            "routing_key": message.topic,
            "consumer_tag": message.subscription_id,
        },
        body=memory_view,
    )

    message2 = WireV1.from_amqp_message(amqp)
    assert str(message) == str(message2)
    assert message.created_at == message2.created_at
    assert message.reply_to == message2.reply_to
    assert message.subscription_id == message2.subscription_id
    assert message.content_type == message2.content_type
    assert message.body == message2.body
    assert message.status == message2.status
    assert message.topic == message2.topic
    assert message.correlation_id == message2.correlation_id
    assert message.timeout == message2.timeout
    assert message.metadata == message2.metadata
