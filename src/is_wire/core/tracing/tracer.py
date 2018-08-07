from opencensus.trace import tracer
from ..utils import new_uuid
from opencensus.trace.span_context import SpanContext

# Patch opencensus to allow 64 bit trace ids
import opencensus.trace.span_context
import re
opencensus.trace.span_context.TRACE_ID_PATTERN = re.compile('[0-9a-f]{16}?')
opencensus.trace.span_context._INVALID_TRACE_ID = '0' * 16


class Tracer(object):
    def __init__(self, exporter=None, span_context=None):
        if span_context is None:
            span_context = SpanContext(trace_id=format(new_uuid(), '016x'))

        self.tracer = tracer.Tracer(
            exporter=exporter,
            span_context=span_context,
        )

    def span(self, name='span'):
        return self.tracer.span(name)

    def start_span(self, name='span'):
        return self.tracer.start_span(name)

    def end_span(self):
        return self.tracer.end_span()
