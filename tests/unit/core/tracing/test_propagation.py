import os
import pytest
from is_wire.core.tracing.propagation import TextFormatPropagator
from is_wire.core import Message, Channel, Subscription, Tracer

URI = os.getenv('WIRE_RABBITMQ_URI', 'amqp://guest:guest@localhost:5672')
EXCHANGE = os.getenv('WIRE_DEFAULT_EXCHANGE', 'is')


def test_propagator():
    carrier = {
        'x-b3-sampled': '1',
        'x-b3-traceid': 'f047c6f208eb36ab',
        'x-b3-flags': '0',
        'x-b3-spanid': 'ef81a2f9c261473d',
        'x-b3-parentspanid': '0000000000000000'
    }

    propagator = TextFormatPropagator()
    context = propagator.from_carrier(carrier)
    carrier2 = propagator.to_carrier(context, {})
    assert carrier == carrier2


def test_injection():
    tracer = Tracer()
    with tracer.span(name="span_name") as span:
        message = Message()
        message.inject_tracing(span)

        assert message.metadata['x-b3-sampled'] == '1'
        assert message.metadata['x-b3-traceid'] == str(
            tracer.tracer.span_context.trace_id)
        assert message.metadata['x-b3-flags'] == '0'
        assert message.metadata['x-b3-spanid'] == str(span.span_id)
        assert message.metadata['x-b3-parentspanid'] == '0000000000000000'


def test_extraction():
    message = Message()
    message.metadata['x-b3-sampled'] = '1'
    message.metadata['x-b3-traceid'] = 'f047c6f208eb36ab'
    message.metadata['x-b3-flags'] = '0'
    message.metadata['x-b3-spanid'] = 'ef81a2f9c261473d'
    message.metadata['x-b3-parentspanid'] = '0000000000000000'

    context = message.extract_tracing()
    assert context.trace_id == 'f047c6f208eb36ab'
    assert context.span_id == 'ef81a2f9c261473d'


def test_propagation():
    topic = "span_test"
    channel = Channel(uri=URI, exchange=EXCHANGE)
    subscription = Subscription(channel)
    subscription.subscribe(topic)

    tracer = Tracer()
    with tracer.span(name="span_name") as span:
        span_id = span.span_id
        message = Message()
        message.body = "body".encode('latin1')
        message.inject_tracing(span)
        channel.publish(topic=topic, message=message)

    message2 = channel.consume(timeout=1.0)
    span_context = message2.extract_tracing()

    assert span_context.span_id == span_id
    assert span_context.trace_id == tracer.tracer.span_context.trace_id