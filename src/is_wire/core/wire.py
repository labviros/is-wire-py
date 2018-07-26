from is_msgs import wire_pb2

from .message import Message


def content_type_to_wire(content_type):
    """ Converts an object of type ContentType to the wire string representation.
    Args:
        content_type (ContentType): enum value
    Returns:
        str: wire string representation
    """
    if content_type == wire_pb2.ContentType.Value("PROTOBUF"):
        return 'application/x-protobuf'

    if content_type == wire_pb2.ContentType.Value("JSON"):
        return 'application/json'

    raise NotImplementedError(
        "ContentType '{}' wire serialization not implemented".format(
            wire_pb2.ContentType.Name(content_type)))


def content_type_from_wire(string):
    """ Converts the ContentType wire string representation to the enum form.
    Args:
        string (str): wire string representation
    Returns:
        ContentType: enum value
    """
    if string == 'application/x-protobuf':
        return wire_pb2.ContentType.Value("PROTOBUF")

    if string == 'application/json':
        return wire_pb2.ContentType.Value("JSON")

    raise RuntimeError("Bad content_type {}".format(string))


class WireV1(object):
    @staticmethod
    def from_amqp_message(amqp):
        message = Message()
        message.body = amqp.body.tobytes()

        delivery_info = amqp.delivery_info
        message.topic = delivery_info["routing_key"]
        message.subscription_id = delivery_info["consumer_tag"]

        properties = amqp.properties
        if "content_type" in properties:
            message.content_type = content_type_from_wire(
                properties["content_type"])
        if "correlation_id" in properties:
            message.correlation_id = int(properties["correlation_id"])
        if "reply_to" in properties:
            message.reply_to = properties["reply_to"]
        if "expiration" in properties:
            message.timeout = int(properties["expiration"])
        if "timestamp" in properties:
            message.created_at = properties["timestamp"] / 1000.0
        if "headers" in properties:
            message.metadata = properties["headers"]

        return message

    @staticmethod
    def to_amqp_properties(message):
        properties = {}
        if message.has_content_type():
            properties["content_type"] = content_type_to_wire(
                message.content_type)
        if message.has_correlation_id():
            properties["correlation_id"] = str(message.correlation_id)
        if message.has_reply_to():
            properties["reply_to"] = message.reply_to
        if message.has_timeout():
            properties["expiration"] = str(int(message.timeout * 1000))
        if not len(message.metadata) is 0:
            properties["headers"] = message.metadata

        properties["timestamp"] = int(message.created_at * 1000)
        return properties
