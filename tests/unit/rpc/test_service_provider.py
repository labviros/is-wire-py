from is_wire.rpc import ServiceProvider, LogInterceptor
from is_wire.core import Channel, Status, StatusCode, Subscription, Message
from google.protobuf.struct_pb2 import Struct
from google.protobuf.wrappers_pb2 import Int64Value


def my_service(request, context):
    value = int(request.fields["value"].number_value)
    if value == 666:
        return Status(StatusCode.FAILED_PRECONDITION, "Cant be zero")
    if value == 10:
        raise RuntimeError("Unexpected error")
    reply = Int64Value(value=value)
    return reply


def test_rpc():
    channel = Channel()
    service = ServiceProvider(channel)
    service.add_interceptor(LogInterceptor())
    service.delegate("MyService", my_service, Struct, Int64Value)

    subscription = Subscription(channel)

    def request_serve_consume(number):
        struct = Struct()
        struct.fields["value"].number_value = number
        message = Message(struct)
        message.reply_to = subscription
        message.pack(struct)
        channel.publish(topic="MyService", message=message)

        request = channel.consume(timeout=1.0)
        assert request.body == message.body
        service.serve(request)
        assert request.unpack(Struct) == struct

        return channel.consume(timeout=1.0)

    reply = request_serve_consume(90.0)
    int64 = reply.unpack(Int64Value)
    assert int64.value == 90
    assert reply.status.ok() is True

    reply = request_serve_consume(666.0)
    assert reply.status.ok() is False
    assert reply.status.code == StatusCode.FAILED_PRECONDITION

    reply = request_serve_consume(10.0)
    assert reply.status.ok() is False
    assert reply.status.code == StatusCode.INTERNAL_ERROR
