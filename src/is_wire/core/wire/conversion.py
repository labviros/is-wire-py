from ..message import Message
from .content_type import content_type_from_wire, content_type_to_wire
from .status import Status, StatusCode
from . import wire_pb2
from google.protobuf import json_format
from six import binary_type


class WireV1(object):
    @staticmethod
    def from_amqp_message(amqp_message):
        message = Message()

        if not isinstance(amqp_message.body, binary_type):
            message.body = amqp_message.body.encode('latin')
        else:
            message.body = amqp_message.body

        delivery_info = amqp_message.delivery_info
        message.topic = delivery_info["routing_key"]
        message.subscription_id = delivery_info["consumer_tag"]

        properties = amqp_message.properties
        if "content_type" in properties:
            message.content_type = content_type_from_wire(
                properties["content_type"])

        if "correlation_id" in properties:
            message.correlation_id = int(properties["correlation_id"], 16)

        if "reply_to" in properties:
            message.reply_to = properties["reply_to"]

        if "expiration" in properties:
            message.timeout = int(properties["expiration"]) / 1000.0

        if "timestamp" in properties:
            message.created_at = properties["timestamp"] / 1000.0

        if "application_headers" in properties:
            if "rpc-status" in properties["application_headers"]:
                status = json_format.Parse(
                    properties["application_headers"]["rpc-status"],
                    wire_pb2.Status())
                message.status = Status(
                    code=StatusCode(status.code),
                    why=status.why,
                )
                del properties["application_headers"]["rpc-status"]

            message.metadata = properties["application_headers"]

        return message

    @staticmethod
    def to_amqp_properties(message):
        properties = {}
        properties["timestamp"] = int(message.created_at * 1000)

        if message.has_content_type():
            properties["content_type"] = content_type_to_wire(
                message.content_type)

        if message.has_correlation_id():
            properties["correlation_id"] = "{:X}".format(
                message.correlation_id)

        if message.has_reply_to():
            properties["reply_to"] = message.reply_to

        if message.has_timeout():
            properties["expiration"] = str(int(message.timeout * 1000))

        if len(message.metadata) != 0:
            properties["application_headers"] = message.metadata
        else:
            properties["application_headers"] = {}

        if message.has_status():
            status = wire_pb2.Status(
                code=message.status.code.value,
                why=message.status.why,
            )
            properties["application_headers"][
                "rpc-status"] = json_format.MessageToJson(
                    status, indent=0, including_default_value_fields=True)

        return properties
