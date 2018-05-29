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
                context.update({
                    'x-b3-sampled': u'1',
                    'x-b3-traceid': unicode(span_context.trace_id),
                    'x-b3-flags': u'0',
                    'x-b3-spanid': unicode(new_span_id),
                    'x-b3-parentspanid': u'0000000000000000'
                })
                f(msg, context)
                tracer.end_span()
            return wrapper
        return interceptor_dec