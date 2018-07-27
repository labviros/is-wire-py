from is_wire.core import Channel, Message, Subscription, ContentType, now
from google.protobuf.struct_pb2 import Struct

import pytest


def test_channel():
    channel = Channel()

    subscription = Subscription(channel)
    subscription.subscribe("MyTopic.Sub.Sub")

    struct = Struct()
    struct.fields["key"].number_value = 1021892179281291921898928198

    sent = Message(struct)
    sent.reply_to = subscription
    sent.created_at = int(1000 * now()) / 1000.0
    sent.timeout = 1.0
    sent.topic = "MyTopic.Sub.Sub"

    channel.publish(message=sent)

    received = channel.consume(timeout=1.0)
    struct2 = received.unpack(Struct)

    assert str(struct) == str(struct2)
    assert struct == struct2

    assert sent.reply_to == received.reply_to
    assert sent.subscription_id == received.subscription_id
    assert sent.content_type == received.content_type
    assert sent.body == received.body
    assert sent.status == received.status
    assert sent.topic == received.topic
    assert sent.correlation_id == received.correlation_id
    assert sent.timeout == received.timeout
    assert sent.metadata == received.metadata
    # Not passing, librabbitmq issue https://github.com/celery/librabbitmq/issues/79
    # assert sent.created_at == received.created_at
