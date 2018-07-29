from is_wire.rpc import ServiceProvider, LogInterceptor
from is_wire.core import Channel, Status, StatusCode, Subscription, \
  Message, ContentType
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp


def my_service(request, context):
    value = int(request.fields["value"].number_value)
    if value == 0:
        return Status(StatusCode.FAILED_PRECONDITION)
    if value == 10:
        raise RuntimeError()
    reply = Timestamp(seconds=value)
    return reply


def test_rpc():
    channel = Channel()
    service = ServiceProvider(channel)
    service.add_interceptor(LogInterceptor())
    service.delegate("MyService", my_service, Struct, Timestamp)

    subscription = Subscription(channel)

    struct = Struct()
    struct.fields["value"].number_value = 90

    def request_serve_consume():
        channel.publish(
            topic="MyService",
            message=Message(
                content=struct,
                reply_to=subscription,
                content_type=ContentType.JSON,
            ),
        )
        request = channel.consume()
        service.serve(request)
        return channel.consume()

    reply = request_serve_consume()
    timestamp = reply.unpack(Timestamp)
    assert struct.fields["value"].number_value == timestamp.seconds
    assert reply.status.ok() is True

    struct.fields["value"].number_value = 0
    reply = request_serve_consume()
    assert reply.status.ok() is False
    assert reply.status.code == StatusCode.FAILED_PRECONDITION

    struct.fields["value"].number_value = 10
    reply = request_serve_consume()
    assert reply.status.ok() is False
    assert reply.status.code == StatusCode.INTERNAL_ERROR
