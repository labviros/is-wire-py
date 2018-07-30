from ..core import Logger, Tracer
from ..rpc import Interceptor


class TracingInterceptor(Interceptor):
    def __init__(self, exporter):
        self.log = Logger(name='TracingInterceptor')
        self.exporter = exporter

    def before_call(self, context):
        self.tracer = Tracer(
            self.exporter, span_context=context.request.extract_tracing())
        self.tracer.start_span()

    def after_call(self, context):
        self.tracer.end_span()
