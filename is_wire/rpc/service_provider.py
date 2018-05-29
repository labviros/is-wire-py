import sys

from ..core import Channel, Subscription, Message
from ..core.utils import current_time

class ServiceProvider:
    def __init__(self, channel):
        self.__channel = channel
        self.__interceptors = []
       
    def __deadline_exceeded(self, msg):
        dt = current_time() - msg.created_at()
        return not dt < int(msg.timeout_ms())

    def add_interceptor(self, interceptor):
        self.__interceptors.append(interceptor)

    def delegate(self, service, request_pb, reply_pb, service_impl):
        subscription = Subscription(self.__channel, service)
        def wrapper(request_msg, context):
            context['service_name'] = service
            for intc in self.__interceptors:
                context = intc.before_call(context)
            
            request = request_msg.unpack(request_pb)
            reply = None
            status = {'code': '', 'why': ''}
            if request:
                try:
                    if not self.__deadline_exceeded(request_msg):
                        reply, status = service_impl(request)
                except Exception as ex:
                    status['code'] = 'INTERNAL_ERROR'
                    status['why'] = 'Service \'{}\' throwed an exception: \'{}\''.format(service, ex)
                except:
                    status['code'] = 'INTERNAL_ERROR'
                    status['why'] = 'Service \'{}\' throwed unkown exception of type \'{}\''.format(service, sys.exc_info()[0])
            else:
                status['code'] = 'FAILED_PRECONDITION' 
                status['why'] = 'Expected request type \'{}\' but received something else'.format(request_pb.DESCRIPTOR.full_name)
            
            timeouted = self.__deadline_exceeded(request_msg)
            if timeouted:
                status['code'] = 'DEADLINE_EXCEEDED'
                status['why'] = ''
                     
            context['rpc-status'] = status
            for intc in self.__interceptors:
                context = intc.after_call(context)
            
            if not timeouted:
                reply_msg = request_msg.create_reply()
                reply_msg.pack(reply).add_metadata({'rpc-status': status})
                self.__channel.publish(reply_msg)

        on_request = wrapper
        tracer = self.__channel.tracer()
        if tracer:
            on_request = tracer.interceptor(service)(on_request)
    
        subscription.subscribe(service, on_request)