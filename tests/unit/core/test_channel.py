from is_wire.core import Channel, Message, Subscription
from google.protobuf.struct_pb2 import Struct

import pytest


def test_channel():
    channel = Channel()

    subscription = Subscription(channel)
    subscription.subscribe("MyTopic.Sub.Sub")

    struct = Struct()
    struct.fields["key"].number_value = 10

    channel.publish(topic="MyTopic.Sub.Sub", message=Message(struct))

    message = channel.consume(timeout=1.0)
    received = message.unpack(Struct)

    assert str(struct) == str(received)
    assert struct == received
