from is_wire.core import Message, now
from is_wire.core.wire import WireV1
import six
import librabbitmq
import pytest


def test_amqp_conversion():
    message = Message()
    message.created_at = int(now() * 1000) / 1000.0
    message.reply_to = "reply_to"
    message.subscription_id = "subscription_id"
    message.content_type = "json"
    message.body = '{"field":"value"}'
    message.topic = "MyTopic"

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

    assert str(message) == str(WireV1.from_amqp_message(amqp))
    assert message == WireV1.from_amqp_message(amqp)
