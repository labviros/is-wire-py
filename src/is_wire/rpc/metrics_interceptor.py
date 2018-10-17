from prometheus_client import start_http_server, Counter
from ..rpc import Interceptor
from ..core import Logger
import time


class MetricsInterceptor(Interceptor):
    def __init__(self):
        self.log = Logger(name='MetricsInterceptor')
        labels = ("service", "status_code")
        self.duration = Counter("rpc_duration_total",
                                "How long requests took in seconds", labels)
        self.count = Counter("rpc_count_total",
                             "How many requests were processed", labels)


    def start_server(self, port=8000):
        start_http_server(port)

    def before_call(self, context):
        self.begin = time.time()

    def after_call(self, context):
        took = time.time() - self.begin
        topic = context.request.topic
        code = context.reply.status.code.name
        self.duration.labels(topic, code).inc(took)
        self.count.labels(topic, code).inc()
