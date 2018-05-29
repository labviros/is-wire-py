from .utils import consumer_id

class Subscription:
    def __init__(self, channel, queue=None):
        self.__channel = channel
        self.__ctag = consumer_id() if queue else self.__channel._Channel__ctag
        self.__queue = queue if queue else self.__ctag
        self.__channel._Channel__queue_declare(queue=self.__queue)
        self.__channel._Channel__queue_bind(queue=self.__queue, routing_key=self.__queue)
        self.__channel._Channel__basic_consume(queue=self.__queue, consumer_tag=self.__ctag)

    def name(self):
        return self.__queue

    def id(self):
        return self.__ctag

    def subscribe(self, topic, fn):
        self.__channel._Channel__queue_bind(
            queue=self.__queue, routing_key=topic)
        self.__channel._Channel__subscriptions[self.__ctag][topic] = fn