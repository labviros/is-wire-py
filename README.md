
# Wire

Pub/Sub middleware for the *is* architecture (python implementation)

![PyPI](https://img.shields.io/pypi/v/is-wire.svg?label=is-wire&style=for-the-badge)

## Installation 

Install the wire package using `pip` or `pipenv`:

```shell
  pip install --user is-wire
  # or
  pipenv install --user is-wire
```

## Usage

### Prepare environment

In order to send/receive messages an amqp broker is necessary, to create one simply run:

```shell
docker run -d --rm -p 5672:5672 -p 15672:15672 rabbitmq:3.7.6-management
```

### Basic send/receive

Create a channel to connect to a broker, create a subscription and subscribe to desired topics to receive messages:

```python
from __future__ import print_function
from is_wire.core import Channel, Subscription

# Connect to the broker
channel = Channel("amqp://guest:guest@localhost:5672")

# Subscribe to the desired topic(s)
subscription = Subscription(channel)
subscription.subscribe(topic="MyTopic.SubTopic")
# ... subscription.subscribe(topic="Other.Topic")

# Blocks forever waiting for one message from any subscription
message = channel.consume()
print(message)
```

Create and publish messages:

```python
from is_wire.core import Channel, Message

# Connect to the broker
channel = Channel("amqp://guest:guest@localhost:5672")

message = Message()
# Body is a binary field therefore we need to encode the string
message.body = "Hello!".encode('latin1')

# Broadcast message to anyone interested (subscribed)
channel.publish(message, topic="MyTopic.SubTopic")
```

Serialize/Deserialize protobuf objects:

```python
from is_wire.core import Channel, Message, Subscription, ContentType
from google.protobuf.struct_pb2 import Struct

channel = Channel("amqp://guest:guest@localhost:5672")

subscription = Subscription(channel)
subscription.subscribe(topic="MyTopic.SubTopic")

struct = Struct()
struct.fields["apples"].string_value = "red"

message = Message()
message.content_type = ContentType.JSON # or ContentType.PROTOBUF
message.pack(struct) # Serialize the struct into the message body

channel.publish(message, topic="MyTopic.SubTopic")

# Blocks forever waiting for the message we just sent
received_message = channel.consume()
# Deserialize the struct from the message body
received_struct = received_message.unpack(Struct) 

# Check that they are equal
assert struct == received_struct
```

### Basic Request/Reply 

Create a RPC Server:

```python
from is_wire.core import Channel, StatusCode, Status
from is_wire.rpc import ServiceProvider, LogInterceptor
from google.protobuf.struct_pb2 import Struct
import time


def increment(struct, ctx):
    if struct.fields["value"].number_value < 0:
        # Return error to client
        return Status(StatusCode.INVALID_ARGUMENT, "Number must be positive")

    time.sleep(0.2)  # Simulate work
    struct.fields["value"].number_value += 1.0
    # Return normal reply
    return struct


channel = Channel("amqp://guest:guest@localhost:5672")

provider = ServiceProvider(channel)
logging = LogInterceptor()  # Log requests to console
provider.add_interceptor(logging)

provider.delegate(
    topic="MyService.Increment",
    function=increment,
    request_type=Struct,
    reply_type=Struct)

provider.run() # Blocks forever processing requests
```

Send a request to the RPC Server:

```python
from __future__ import print_function
from is_wire.core import Channel, Message, Subscription
from google.protobuf.struct_pb2 import Struct
import socket

channel = Channel("amqp://guest:guest@localhost:5672")
subscription = Subscription(channel)

# Prepare request
struct = Struct()
struct.fields["value"].number_value = 1.0
request = Message(content=struct, reply_to=subscription)
# Make request
channel.publish(request, topic="MyService.Increment")

# Wait for reply with 1.0 seconds timeout
try:
    reply = channel.consume(timeout=1.0)
    struct = reply.unpack(Struct)
    print('RPC Status:', reply.status, '\nReply:', struct)
except socket.timeout:
    print('No reply :(')
```

### Tracing messages

Instantiate an Exporter to trace requests:

```python
from is_wire.core import ZipkinExporter, BackgroundThreadTransport

# Create an exporter, change values accordingly to match your zipkin server
exporter = ZipkinExporter(
    service_name="MyService",
    host_name="localhost",
    port=9411,
    transport=BackgroundThreadTransport,
)
```

Then create a tracer and start tracing:

```python
from is_wire.core import Channel, Message, Tracer

channel = Channel("amqp://guest:guest@localhost:5672") 
tracer = Tracer(exporter)

with tracer.span(name="publish") as span:
    message = Message()
    # ...
    # Propagates the current tracing context
    message.inject_tracing(span) 
    channel.publish(message, topic="Any.Topic")
```
Or create a tracing interceptor and pass it to your ServiceProvider:

```python
from is_wire.rpc import TracingInterceptor, ServiceProvider

channel = Channel("amqp://guest:guest@localhost:5672") 

provider = ServiceProvider(channel)

tracing = TracingInterceptor(exporter)  # automatically trace requests
provider.add_interceptor(tracing)
```

## Development

### Tests

```shell
# prepare environment
pip install --user tox
docker run -d --rm -p 5672:5672 -p 15672:15672 rabbitmq:3.7.6-management

# run all the tests
tox
```
