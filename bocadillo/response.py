from typing import Tuple, Dict, AnyStr

from starlette.requests import Request
from starlette.responses import Response as _Response


Headers = Dict
Body = AnyStr


class Response:
    """Response builder."""

    def __init__(self, request: Request):
        self.request = request
        self.content: str = None
        self.status_code: int = None

    @property
    async def contents(self) -> Tuple[Body, Headers]:
        if self.content is not None:
            return self.content, {}
        else:
            return '{}', {'Content-Type': 'application/json'}

    async def __call__(self, receive, send):
        """Build and send the response."""
        if self.status_code is None:
            self.status_code = 200

        body, headers = await self.contents
        response = _Response(
            content=body,
            headers=headers,
            status_code=self.status_code,
        )
        await response(receive, send)
