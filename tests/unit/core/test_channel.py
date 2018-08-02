import pytest
from is_wire.core import Channel, Message, Subscription, now
from google.protobuf.struct_pb2 import Struct
import socket


def test_channel():
    channel = Channel()
    subscription = Subscription(channel)
    subscription.subscribe("MyTopic.Sub.Sub")

    struct = Struct()
    struct.fields["value"].number_value = 666.0

    sent = Message(struct)
    sent.reply_to = subscription
    sent.created_at = int(1000 * now()) / 1000.0
    sent.timeout = 1.0
    sent.topic = "MyTopic.Sub.Sub"

    channel.publish(message=sent)
    received = channel.consume(timeout=1.0)

    assert sent.reply_to == received.reply_to
    assert sent.subscription_id == received.subscription_id
    assert sent.content_type == received.content_type
    assert sent.body == received.body
    assert sent.status == received.status
    assert sent.topic == received.topic
    assert sent.correlation_id == received.correlation_id
    assert sent.timeout == received.timeout
    assert sent.metadata == received.metadata
    assert sent.created_at == received.created_at
    assert str(sent) == str(received)

    struct2 = received.unpack(Struct)
    assert str(struct) == str(struct2)
    assert struct == struct2

    channel.close()


@pytest.mark.parametrize("size", [0, 1e4])
def test_body(size):
    channel = Channel()

    subscription = Subscription(channel)
    subscription.subscribe("MyTopic.Sub.Sub")

    sent = Message()
    sent.reply_to = subscription
    sent.topic = "MyTopic.Sub.Sub"
    sent.body = bytes(bytearray(range(256)) * int(size))

    channel.publish(message=sent)
    received = channel.consume(timeout=1.0)

    assert repr(sent.body) == repr(received.body)
    assert sent.body == received.body

    channel.close()


def test_negative_timeout():
    channel = Channel()
    with pytest.raises(AssertionError):
        channel.consume(timeout=-1e-10)
    with pytest.raises(socket.timeout):
        channel.consume(timeout=0)
    channel.close()


def test_empty_topic():
    channel = Channel()
    message = Message(content="body".encode('latin'))

    with pytest.raises(RuntimeError):
        channel.publish(message)

    with pytest.raises(RuntimeError):
        channel.publish(message, topic="")

    subscription = Subscription(channel)
    channel.publish(message, topic=subscription.name)
    recv = channel.consume(timeout=1.0)
    assert recv.body == message.body

    message.topic = subscription.name
    channel.publish(message)
    recv = channel.consume(timeout=1.0)
    assert recv.body == message.body
    channel.close()


def test_multi_subscription():
    channel = Channel()
    message = Message()
    subscription1 = Subscription(channel)
    subscription2 = Subscription(channel)

    channel.publish(message, topic=subscription1.name)
    recv = channel.consume(timeout=1.0)
    assert recv.subscription_id == subscription1.name

    channel.publish(message, topic=subscription2.name)
    recv = channel.consume(timeout=1.0)
    assert recv.subscription_id == subscription2.name
    channel.close()
