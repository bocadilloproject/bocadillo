import json
from typing import Tuple, Dict, AnyStr

from starlette.requests import Request
from starlette.responses import Response as _Response


Headers = Dict
Body = AnyStr


class Response:
    """Response builder."""

    def __init__(self, request: Request):
        self.request = request
        self.content: AnyStr = None
        self.media: dict = None
        self.status_code: int = None
        self.headers = {}

    def _set_json(self, value: dict):
        self.headers['Content-Type'] = 'application/json'
        self.content = json.dumps(value)

    @property
    def _body(self) -> Body:
        """Return the response body.

        Also set the Content-Type header if necessary.
        """
        if self.media is not None:
            self._set_json(self.media)

        if self.content is None:
            self._set_json({})

        self.headers.setdefault('Content-Type', 'text/plain')
        return self.content

    async def __call__(self, receive, send):
        """Build and send the response."""
        if self.status_code is None:
            self.status_code = 200

        body = self._body
        headers = self.headers

        response = _Response(
            content=body,
            headers=headers,
            status_code=self.status_code,
        )
        await response(receive, send)
