from ..utils import assert_type
from . import wire_pb2
from enum import Enum
from six import string_types


class StatusCode(Enum):
    UNKNOWN = wire_pb2.StatusCode.Value('UNKNOWN')
    OK = wire_pb2.StatusCode.Value('OK')
    CANCELLED = wire_pb2.StatusCode.Value('CANCELLED')
    INVALID_ARGUMENT = wire_pb2.StatusCode.Value('INVALID_ARGUMENT')
    DEADLINE_EXCEEDED = wire_pb2.StatusCode.Value('DEADLINE_EXCEEDED')
    NOT_FOUND = wire_pb2.StatusCode.Value('NOT_FOUND')
    ALREADY_EXISTS = wire_pb2.StatusCode.Value('ALREADY_EXISTS')
    PERMISSION_DENIED = wire_pb2.StatusCode.Value('PERMISSION_DENIED')
    UNAUTHENTICATED = wire_pb2.StatusCode.Value('UNAUTHENTICATED')
    FAILED_PRECONDITION = wire_pb2.StatusCode.Value('FAILED_PRECONDITION')
    OUT_OF_RANGE = wire_pb2.StatusCode.Value('OUT_OF_RANGE')
    UNIMPLEMENTED = wire_pb2.StatusCode.Value('UNIMPLEMENTED')
    INTERNAL_ERROR = wire_pb2.StatusCode.Value('INTERNAL_ERROR')


class Status(object):
    def __init__(self, code=StatusCode.UNKNOWN, why=""):
        self._code = None
        self._why = None
        self.code = code
        self.why = why

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        pretty = "{{ code={} why='{}' }}".format(self.code, self.why or "")
        return pretty

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        assert_type(code, StatusCode, "code")
        self._code = code

    def ok(self):
        return self._code == StatusCode.OK

    @property
    def why(self):
        return self._why

    @why.setter
    def why(self, reason):
        assert_type(reason, string_types, "why")
        self._why = reason
