from ..core import Logger, Tracer
from ..rpc import Interceptor


def service_name(context):
    return context.request.topic.split(".")[-1]


class TracingInterceptor(Interceptor):
    def __init__(self, exporter, span_namer=service_name):
        """ Construct a TracingInterceptor to automatically trace requests
        of a ServiceProvider.
        Args:
            exporter (opencensus.Exporter): object responsible for exporting
            spans to a tracer.
            span_namer (function: Context -> str): function responsible
            for generating the name of the request span.
        """
        self.log = Logger(name='TracingInterceptor')
        self.exporter = exporter
        self.namer = span_namer

    def before_call(self, context):
        self.tracer = Tracer(
            self.exporter, span_context=context.request.extract_tracing())
        context.addons["tracer"] = self.tracer
        self.span = self.tracer.start_span(name=self.namer(context))

    def after_call(self, context):
        status = context.reply.status
        if not status.ok():
            self.span.add_attribute("reply_to", context.request.reply_to)
            self.span.add_attribute("status_code", status.code.name)
            self.span.add_attribute("status_why", status.why)

        context.reply.inject_tracing(self.span)
        self.tracer.end_span()
