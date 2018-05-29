import pika
import uuid
import json
from collections import defaultdict
from threading import Timer

from .subscription import Subscription
from .message import Message
from .utils import current_time, consumer_id
from .logger import Logger

class Channel(object):
    def __init__(self, hostname='localhost', port=5672):
        params = pika.ConnectionParameters(hostname, port)
        self.__connection = pika.BlockingConnection(params)
        self.__amqp_channel = self.__connection.channel()
        self.__exchange = 'is'
        self.__queues = []
        self.__ctag = consumer_id()
        self.__ctags = []
        self.__subscription = Subscription(self)
        self.__subscriptions = defaultdict(dict)
        self.__rpcs = defaultdict(dict)
        self.__timers = defaultdict(dict)
        self.__log = Logger(name='__channel__')
        self.__tracer = None

    def __on_message(self, channel, method, props, body):
        rkey = method.routing_key
        ctag = method.consumer_tag
        cid = props.correlation_id
        msg = Message()
        msg.set_body(body)
        msg.set_properties(props)
        if rkey in self.__subscriptions[ctag]:
            self.__subscriptions[ctag][rkey](msg, {})
        elif rkey in self.__queues:
            if cid in self.__timers[ctag]:
                self.__timers[ctag][cid].cancel()
                del self.__timers[ctag][cid]
            if cid in self.__rpcs[ctag]:
                self.__rpcs[ctag][cid](msg, {})
                del self.__rpcs[ctag][cid]
            else:
                self.__log.warn('Message to {} with CID {} with no callback assigned or removed due timeout', rkey, ctag)

    def __queue_bind(self, queue, routing_key):
        self.__amqp_channel.queue_bind(exchange=self.__exchange, queue=queue, routing_key=routing_key)
    
    def __queue_declare(self, queue):
        if not queue in self.__queues:
            self.__queues.append(queue)
            self.__amqp_channel.queue_declare(queue=queue, exclusive=False, durable=False, auto_delete=True, passive=False)

    def __basic_consume(self, queue, consumer_tag, callback=None):
        if not consumer_tag in self.__ctags:
            callback = self.__on_message if not callback else callback
            self.__amqp_channel.basic_consume(callback, queue=queue, consumer_tag=consumer_tag, no_ack=True)
            self.__ctags.append(consumer_tag)

    def __default_on_timetout(self, msg, context):
        self.__log.warn('Request to {} failed: deadline excedeed for message with cid: {}', msg.topic(), msg.correlation_id())

    def set_tracer(self, tracer):
        self.__tracer = tracer

    def tracer(self):
        return self.__tracer

    def publish(self, msg):
        if msg.has_reply_to() and msg.has_consumer_tag() and msg.has_correlation_id() and msg.has_on_reply():
            cid = msg.correlation_id()
            ctag = msg.consumer_tag()
            self.__rpcs[ctag][cid] = msg.on_reply()
            if msg.has_timeout_ms():
                on_timeout = msg.on_timeout() if msg.has_on_timeout() else self.__default_on_timetout
                def handle(msg, context):
                    cid = msg.correlation_id()
                    ctag = msg.consumer_tag()
                    if cid in self.__rpcs[ctag]:
                        del self.__rpcs[ctag][cid]
                        on_timeout(msg, context)
                timer = Timer(int(msg.timeout_ms()) / 1000.0, handle, [msg, {}])
                timer.start()
                self.__timers[ctag][cid] = timer
        
        self.__amqp_channel.basic_publish(self.__exchange, msg.topic(), msg.body(), msg.get_properties())

    def listen(self):
        self.__amqp_channel.start_consuming()