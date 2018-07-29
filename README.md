
# Wire - Pub/Sub middleware for the *is* architecture (python implementation)


## Installation 

Install the wire package using `pip` or `pipenv`:

```shell
  pip install --user is-wire
  pipenv install --user is-wire
```

## Usage

In order to send/receive messages an amqp broker is necessary, to create one simply run:

```shell
docker run -d --rm -p 5672:5672 -p 15672:15672 rabbitmq:3.7.6-management
```

Create a channel to connect to a broker, create a subscription and subscribe to desired topics to receive messages:

```python
from __future__ import print_function
from is_wire.core import Channel, Subscription

channel = Channel("amqp://guest:guest@localhost:5672")

subscription = Subscription(channel)
subscription.subscribe(topic="MyTopic.SubTopic")

message = channel.consume()
print(message)
```

Create and publish messages:

```python
from is_wire.core import Channel, Message

channel = Channel("amqp://guest:guest@localhost:5672")

message = Message()
message.body = "Hello!"

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
message.pack(struct)

channel.publish(message, topic="MyTopic.SubTopic")

received_message = channel.consume(timeout=1.0)
received_struct = received_message.unpack(Struct)

assert struct == received_struct
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
