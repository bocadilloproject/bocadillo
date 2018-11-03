class Route:

    def __init__(self, handler):
        self._handler = handler

    def handle(self, request, receive, send):
        self._handler(request)
