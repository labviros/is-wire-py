import amqp
from six.moves import urllib
from .wire.conversion import WireV1


class Channel(object):
    def __init__(self, uri="amqp://guest:guest@localhost:5672"):
        url = urllib.parse.urlparse(uri)

        self.connection = amqp.Connection(
            host="{}:{}".format(url.hostname or "localhost", url.port or 5672),
            userid=url.username or "guest",
            password=url.password or "guest",
            connect_timeout=5.0,
        )
        self.connection.connect()

        self._channel = self.connection.channel()
        self._channel.auto_decode = False

        self._exchange = "is"
        self._channel.exchange_declare(
            exchange=self._exchange,
            type="topic",
            durable=False,
            auto_delete=False,
        )

        self.subscriptions = []
        self.amqp_message = None

    def _on_message(self, message):
        self.amqp_message = message

    def publish(self, message, topic=None):
        """ Publishes a message to the given topic. The topic on the message
        is used when no topic is passed to this function. If no valid topic is
        passed a RuntimeError is raised."""
        if not message.has_topic() and not topic:
            raise RuntimeError("Trying to publish message without topic")

        amqp_message = amqp.Message(
            body=message.body,
            channel=self._channel,
            **WireV1.to_amqp_properties(message))

        self._channel.basic_publish(
            amqp_message,
            exchange=self._exchange,
            routing_key=message.topic if topic is None else topic,
            immediate=False,
            mandatory=False,
        )

    def consume(self, timeout=None):
        """ Blocks waiting for a new message to arrive. If no timeout
        (in seconds) is provided the function blocks forever.
        Args:
            timeout (float): Period in seconds to block waiting for messages.
            Must be a positive number. If 0 is passed the call is non-blocking.
            If no message was received after this period a socket.timeout
            Exception is raised.
        Returns:
            Message: Received message.
        """
        if timeout is not None:
            assert timeout >= 0.0

        self.amqp_message = None
        while self.amqp_message is None:
            self.connection.drain_events(timeout)
        return WireV1.from_amqp_message(self.amqp_message)

    def close(self):
        self.connection.close()
