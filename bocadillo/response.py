import json
from typing import AnyStr

from starlette.requests import Request
from starlette.responses import Response as _Response


class Response:
    """Response builder."""

    def __init__(self, request: Request):
        self.request = request
        self._content: AnyStr = None
        self.status_code: int = None
        self.headers = {}

    def __setattr__(self, key, value):
        if key == 'text':
            self.headers['Content-Type'] = 'text/plain'
            self._content = value
        elif key == 'html':
            self.headers['Content-Type'] = 'text/html'
            self._content = value
        elif key == 'media':
            self.headers['Content-Type'] = 'application/json'
            self._content = json.dumps(value)
        elif key == 'content':
            self._content = value
        else:
            super().__setattr__(key, value)

    async def __call__(self, receive, send):
        """Build and send the response."""
        if self.status_code is None:
            self.status_code = 200

        if self.status_code != 204:
            self.headers.setdefault('Content-Type', 'text/plain')

        response = _Response(
            content=self._content,
            headers=self.headers,
            status_code=self.status_code,
        )
        await response(receive, send)
