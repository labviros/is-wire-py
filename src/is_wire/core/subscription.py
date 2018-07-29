from .utils import consumer_id


class Subscription(object):
    def __init__(self, channel, name=None):
        self._id = consumer_id()
        self._name = self._id if name is None else name
        self._topics = set()

        self._channel = channel._channel
        self._exchange = channel._exchange

        def create_queue(channel, exchange, queue, tag, on_message):
            channel.queue_declare(
                queue=queue,
                passive=False,
                durable=False,
                exclusive=False,
                auto_delete=True,
            )

            channel.queue_bind(
                queue=queue,
                exchange=exchange,
                routing_key=queue,
            )

            channel.basic_consume(
                queue=queue,
                callback=on_message,
                consumer_tag=tag,
                no_local=False,
                no_ack=True,
                exclusive=False,
            )

        create_queue(self._channel, self._exchange, self._name, self._id,
                     channel._on_message)

    def subscribe(self, topic):
        """ Subscribes to the given topic.
        Args:
            topic (str): topic to receive messages from.
        """
        self._channel.queue_bind(
            queue=self._name,
            exchange=self._exchange,
            routing_key=topic,
        )
        self._topics.add(topic)

    def unsubscribe(self, topic):
        """ Unsubscribe from the given topic.
        Args:
            topic (str): topic to stop receiving messages from.
        """
        self._channel.queue_unbind(
            queue=self._name,
            exchange=self._exchange,
            routing_key=topic,
        )
        self._topics.remove(topic)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def topics(self):
        return self._topics
