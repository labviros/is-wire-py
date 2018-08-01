class Context(object):
    def __init__(self, request, reply):
        self._request = request
        self._reply = reply
        self._addons = {}

    @property
    def request(self):
        return self._request

    @property
    def reply(self):
        return self._reply

    @property
    def addons(self):
        return self._addons
