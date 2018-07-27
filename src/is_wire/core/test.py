from channel import Channel
from subscription import Subscription

channel = Channel("amqp://10.10.2.20:30000")

subscription = Subscription(channel)
subscription.subscribe("Skeletons.0.Detections")

subscription2 = Subscription(channel)
subscription2.subscribe("Skeletons.1.Detections")

while True:
    print channel.consume()
