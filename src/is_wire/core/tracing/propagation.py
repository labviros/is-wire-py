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

    def from_carrier(self, carrier):
        trace_id = carrier[
            self.trace_id_key] if self.trace_id_key in carrier else None

        span_id = carrier[
            self.span_id_key] if self.span_id_key in carrier else None

        # parent_span_id = carrier[
        #     parent_span_id_key] if parent_span_id_key in carrier else None

        # sampled = carrier[sampled_key] if sampled_key in carrier else None

        return SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            from_header=True,
        )

    def to_carrier(self, span_context, carrier):
        assert_type(span_context, SpanContext, "span_context")
        carrier[self.trace_id_key] = span_context.trace_id

        if span_context.span_id is not None:
            carrier[self.span_id_key] = span_context.span_id

        carrier[self.sampled_key] = '1'
        carrier[self.parent_span_id_key] = '0' * 16
        carrier[self.flags_key] = '0'
        return carrier

    @staticmethod
    def new_span_context(trace_id, span_id):
        return SpanContext(trace_id=trace_id, span_id=span_id)
