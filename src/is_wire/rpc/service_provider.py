from ..core import Channel, Subscription, Status, StatusCode, Logger
from ..core.utils import assert_type
from .interceptor import Interceptor
from .context import Context
import traceback
import six
from google.protobuf.json_format import ParseError


class ServiceProvider(object):
    log = Logger("ServiceProvider", Logger.DEBUG)

    def __init__(self, channel):
        assert_type(channel, Channel, "channel")
        self._channel = channel
        self._services = {}
        self._interceptors = []

    def delegate(self, topic, function, request_type, reply_type):
        """ Bind a function to a particular topic, so everytime a message is
            received in this topic the function will be called """
        assert_type(topic, six.string_types, "topic")
        self.log.debug("New service registered '{}'", topic)
        subscription = Subscription(self._channel, name=topic)
        wrapped = self.wrap(function, request_type, reply_type)
        self._services[subscription.id] = wrapped

    def add_interceptor(self, interceptor):
        if not issubclass(type(interceptor), Interceptor):
            raise TypeError(
                "Interceptors must derive from the Interceptor class")
        self._interceptors.append(interceptor)

    def serve(self, message):
        """ Attempts to serve message """
        if message.subscription_id in self._services:
            reply = self._services[message.subscription_id](message)
            if reply.has_topic():
                self._channel.publish(reply)
        else:
            self.log.debug("Ignoring request\n{}", message.short_string())

    def run(self):
        """ Blocks the current thread listening for requests """
        self.log.info("Listening for requests")
        while True:
            self.serve(self._channel.consume())

    def wrap(self, function, request_type, reply_type):
        def safe_call(*args):
            try:
                return function(*args)
            except Exception:
                return Status(
                    code=StatusCode.INTERNAL_ERROR,
                    why="Service throwed exception:\n{}".format(
                        traceback.format_exc()),
                )

        def run_interceptors(interceptors, method, *args):
            for interceptor in interceptors:
                try:
                    getattr(interceptor, method)(*args)
                except Exception:
                    self.log.warn(
                        "Interceptor '{}' throwed exception:\n{}",
                        type(interceptor).__name__,
                        traceback.format_exc(),
                    )

        def wrapper(request):
            run_interceptors(self._interceptors, "before_call", request)

            reply = request.create_reply()
            try:
                arg = request.unpack(request_type)
                context = Context()
                result = safe_call(arg, context)
                if not isinstance(result, Status):
                    assert_type(result, reply_type, "reply")
                    reply.pack(result)
                    reply.status = Status(code=StatusCode.OK)
                else:
                    reply.status = result
            except ParseError:
                why = "Expected request type '{}' but received something else"\
                    .format(request_type.DESCRIPTOR.full_name)
                reply.status = Status(StatusCode.FAILED_PRECONDITION, why)

            run_interceptors(self._interceptors, "after_call", reply)
            return reply

        return wrapper
