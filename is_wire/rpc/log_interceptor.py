from ..core import Logger
from ..core.utils import current_time

class LogInterceptor:
    def __init__(self):
        self.log = Logger(name='__log_interceptor__')

    def before_call(self, context):
        context['t_start'] = current_time()
        return context

    def after_call(self, context):
        t_start = context['t_start']
        t_end = current_time()
        took = t_end - t_start
        service_name = context['service_name']
        if 'rpc-status' in context:
            status = context['rpc-status']['code']
            why = context['rpc-status']['why'] if 'why' in context['rpc-status'] else ''
            if status.lower() == 'ok':
                self.log.info('{};{}ms;{}', service_name, took, status)
            elif status.lower() == 'internal_error':
                self.log.error('{};{}ms;{};\'{}\'',
                               service_name, took, status, why)
            else:
                self.log.warn('{};{}ms;{};\'{}\'',
                              service_name, took, status, why)
        return context

    def interceptor(self, service_name):
        def interceptor_dec(f):
            def wrapper(msg, context):
                t_start = current_time()
                f(msg, context)
                t_end = current_time()
                took = t_end - t_start
                metadata = msg.metadata()
                if 'rpc-status' in metadata:
                    status = metadata['rpc-status']['code']
                    why = metadata['rpc-status']['why'] if 'why' in metadata['rpc-status'] else ''
                    if status.lower() == 'ok':
                        self.log.info('{};{}ms;{}', service_name, took, status)
                    elif status.lower() == 'internal_error':
                        self.log.error('{};{}ms;{};\'{}\'',
                                       service_name, took, status, why)
                    else:
                        self.log.warn('{};{}ms;{};\'{}\'',
                                      service_name, took, status, why)
            return wrapper
        return interceptor_dec