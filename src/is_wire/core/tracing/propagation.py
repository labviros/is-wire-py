from opencensus.trace.span_context import SpanContext
from ..utils import assert_type

# Patch opencensus to allow 64 bit trace ids
import opencensus.trace.span_context
import re
opencensus.trace.span_context.TRACE_ID_PATTERN = re.compile('[0-9a-f]{16}?')
opencensus.trace.span_context._INVALID_TRACE_ID = '0' * 16


class TextFormatPropagator(object):
    trace_prefix = 'x-b3'
    trace_id_key = '{}-traceid'.format(trace_prefix)
    span_id_key = '{}-spanid'.format(trace_prefix)
    parent_span_id_key = '{}-parentspanid'.format(trace_prefix)
    sampled_key = '{}-sampled'.format(trace_prefix)
    flags_key = '{}-flags'.format(trace_prefix)

    @classmethod
    def from_carrier(cls, carrier):
        if cls.trace_id_key not in carrier or \
           cls.span_id_key not in carrier:
            return None

        trace_id = carrier[cls.trace_id_key]
        span_id = carrier[cls.span_id_key]

        return SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            from_header=True,
        )

    @classmethod
    def to_carrier(cls, span_context, carrier):
        assert_type(span_context, SpanContext, "span_context")
        carrier[cls.trace_id_key] = span_context.trace_id

        if span_context.span_id is not None:
            carrier[cls.span_id_key] = span_context.span_id

        carrier[cls.sampled_key] = '1'
        carrier[cls.parent_span_id_key] = '0' * 16
        carrier[cls.flags_key] = '0'
        return carrier

    @staticmethod
    def new_span_context(trace_id, span_id):
        return SpanContext(trace_id=trace_id, span_id=span_id)
