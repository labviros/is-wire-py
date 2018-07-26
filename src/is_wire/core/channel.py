import librabbitmq
from message import Message
from urlparse import urlparse
from wire import WireV1
from subscription import Subscription


class Channel(object):
    def __init__(self, uri):
        url = urlparse(uri)

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

    def publish(self, message):
        self._channel.basic_publish(
            body=message.body,
            exchange=self._exchange,
            routing_key=message.topic,
            properties=WireV1.to_amqp_properties(message),
        )

    def consume(self, timeout=None):
        self.connection.drain_events(timeout)
        return WireV1.from_amqp_message(self.amqp_message)
