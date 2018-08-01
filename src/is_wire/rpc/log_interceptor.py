from ..core import Logger, now, StatusCode
from ..rpc import Interceptor


class LogInterceptor(Interceptor):
    def __init__(self):
        self.log = Logger(name='LogInterceptor')

    def before_call(self, context):
        self.begin = now()

    def after_call(self, context):
        took = now() - self.begin
        status = context.reply.status
        if status.ok():
            self.log.info("took={}s, code={}", took, status.code.name)
        elif status.code == StatusCode.INTERNAL_ERROR:
            self.log.error('took={}s status={} request={}', took, status,
                           context.request.short_string())
        else:
            self.log.warn('took={}s status={} request={}', took, status,
                          context.request.short_string())
