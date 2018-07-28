from ..core import Logger, now
from ..rpc import Interceptor


class LogInterceptor(Interceptor):
    def __init__(self):
        self.log = Logger(name='LogInterceptor')

    def before_call(self, request):
        self.begin = now()
        self.request = request

    def after_call(self, reply):
        took = now() - self.begin
        status = reply.status
        if status.ok():
            self.log.info("took={}s, code={}", took, status.code.name)
        else:
            self.log.warn(
                'took={}s, request={}, code={}, why="{}"',
                took,
                self.request.short_string(),
                status.code.name,
                status.why,
            )
