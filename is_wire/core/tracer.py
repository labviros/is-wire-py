from opencensus.trace import tracer as tracer_module
from opencensus.trace.exporters.zipkin_exporter import ZipkinExporter
from opencensus.trace.span_context import SpanContext
from opencensus.trace.span import format_span_json

import opencensus.trace.span_context
import re
opencensus.trace.span_context.TRACE_ID_PATTERN = re.compile('[0-9a-f]{16}?')
opencensus.trace.span_context._INVALID_TRACE_ID = '0' * 16

class ZipkinTracer:
    def __init__(self, host_name='localhost', port=9411, service_name='my_service'):
        self.exporter = ZipkinExporter(
            host_name=host_name, port=port, service_name=service_name)
        self.__tracers = {}

    def start_span(self, span_name):
        tracer = tracer_module.Tracer(exporter=self.exporter)
        span = tracer.start_span(span_name)
        trace_id = span_context = tracer.span_context.trace_id
        span_id = format_span_json(span)['spanId']
        self.__tracers[span_id] = tracer
        return self.__trace_wire(trace_id, span_id)

    def end_span(self, span):
        span_id = span['x-b3-spanid']
        if span_id in self.__tracers:
            tracer = self.__tracers[span_id]
            tracer.end_span()
            del self.__tracers[span_id]

    def __trace_wire(self, trace_id, span_id, parents_id='0000000000000000'):
        return {
            'x-b3-sampled': '1',
            'x-b3-traceid': trace_id,
            'x-b3-flags': '0',
            'x-b3-spanid': span_id,
            'x-b3-parentspanid': parents_id
        }

    def interceptor(self, span_name):
        def interceptor_dec(f):
            def wrapper(msg, context):
                metadata = msg.metadata()
                span_context = None
                if 'x-b3-traceid' in metadata.keys() and 'x-b3-spanid' in metadata.keys():
                    trace_id = str(metadata['x-b3-traceid'])
                    span_id = str(metadata['x-b3-spanid'])
                    span_context = SpanContext(trace_id=trace_id, span_id=span_id)
                
                tracer = tracer_module.Tracer(exporter=self.exporter, span_context=span_context)
                span_context = tracer.span_context
                span = tracer.start_span(span_name)
                new_span_id = format_span_json(span)['spanId']
                context.update(self.__trace_wire(span_context.trace_id, new_span_id))
                f(msg, context)
                tracer.end_span()
            return wrapper
        return interceptor_dec