from enum import Enum
from . import wire_pb2
from ..utils import assert_type


class ContentType(Enum):
    PROTOBUF = wire_pb2.ContentType.Value("PROTOBUF")
    JSON = wire_pb2.ContentType.Value("JSON")


def content_type_to_wire(content_type):
    """ Converts an object of type ContentType to the wire string representation.
    Args:
        content_type (ContentType): enum value
    Returns:
        str: wire string representation
    """
    assert_type(content_type, ContentType, "content_type")
    if content_type == ContentType.PROTOBUF:
        return 'application/x-protobuf'

    if content_type == ContentType.JSON:
        return 'application/json'

    raise NotImplementedError(
        "ContentType '{}' wire serialization not implemented".format(
            content_type.name))


def content_type_from_wire(string):
    """ Converts the ContentType wire string representation to the enum form.
    Args:
        string (str): wire string representation
    Returns:
        ContentType: enum value
    """
    assert_type(string, str, "string")
    if string == 'application/x-protobuf':
        return ContentType.PROTOBUF

    if string == 'application/json':
        return ContentType.JSON

    raise RuntimeError("Bad content_type {}".format(string))
