import librabbitmq

from six.moves import urllib
from .wire.conversion import WireV1


class Channel(object):
    def __init__(self, uri="amqp://guest:guest@localhost:5672"):
        url = urllib.parse.urlparse(uri)

        self.connection = librabbitmq.Connection(
            host=url.hostname or "localhost",
            port=url.port or 5672,
            userid=url.username or "guest",
            password=url.password or "guest",
        )

        self._channel = self.connection.channel()
        self._exchange = "is"
        self._channel.exchange_declare(
            exchange=self._exchange, type="topic", durable=True)
        self.subscriptions = []
        self.amqp_message = None

    def _on_message(self, message):
        self.amqp_message = message

    def publish(self, message, topic=None):
        amqp = librabbitmq.Message(
            body=message.body,
            channel=self._channel,
            properties=WireV1.to_amqp_properties(message))

        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=message.topic if topic is None else topic,
            body=amqp,
        )

    def consume(self, timeout=None):
        self.connection.drain_events(timeout)
        return WireV1.from_amqp_message(self.amqp_message)
