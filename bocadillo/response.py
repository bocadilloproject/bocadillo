from typing import AnyStr, Any

from starlette.requests import Request
from starlette.responses import Response as _Response

from bocadillo.media import Media


class Response:
    """Response builder."""

    def __init__(self, request: Request, media: Media):
        self.request = request
        self._content: AnyStr = None
        self.status_code: int = None
        self.headers = {}
        self._media = media

    def _set_media(self, value: Any, media_type: str):
        content = self._media.serialize(value, media_type=media_type)
        self.headers['content-type'] = media_type
        self._content = content

    def __setattr__(self, key, value):
        if key == 'text':
            self._set_media(value, media_type=Media.PLAIN_TEXT)
        elif key == 'html':
            self._set_media(value, media_type=Media.HTML)
        elif key == 'media':
            self._set_media(value, media_type=self._media.type)
        elif key == 'content':
            self._content = value
        else:
            super().__setattr__(key, value)

    async def __call__(self, receive, send):
        """Build and send the response."""
        if self.status_code is None:
            self.status_code = 200

        if self.status_code != 204:
            self.headers.setdefault('content-type', Media.PLAIN_TEXT)

        response = _Response(
            content=self._content,
            headers=self.headers,
            status_code=self.status_code,
        )
        await response(receive, send)
