from typing import AnyStr, Any, Callable, Coroutine, Optional

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import Response as _Response

from .media import Media

BackgroundFunc = Callable[..., Coroutine]


class Response:
    """Response builder."""

    def __init__(self, request: Request, media: Media):
        self.request = request
        self._content: AnyStr = None
        self.status_code: int = None
        self.headers = {}
        self._media = media
        self._background: BackgroundFunc = None

    def _set_media(self, value: Any, media_type: str):
        content = self._media.serialize(value, media_type=media_type)
        self.headers["content-type"] = media_type
        self._content = content

    @property
    def content(self) -> Optional[AnyStr]:
        return self._content

    @content.setter
    def content(self, content: AnyStr):
        self._content = content

    def __setattr__(self, key, value):
        if key == "text":
            self._set_media(value, media_type=Media.PLAIN_TEXT)
        elif key == "html":
            self._set_media(value, media_type=Media.HTML)
        elif key == "media":
            self._set_media(value, media_type=self._media.type)
        else:
            super().__setattr__(key, value)

    def background(self, func: BackgroundFunc, *args, **kwargs):
        """Register a coroutine function to be executed in the background."""

        async def background():
            await func(*args, **kwargs)

        self._background = background
        return func

    @property
    def background_task(self) -> Optional[BackgroundTask]:
        if self._background is not None:
            return BackgroundTask(self._background)
        return None

    async def __call__(self, receive, send):
        """Build and send the response."""
        if self.status_code is None:
            self.status_code = 200

        if self.status_code != 204:
            self.headers.setdefault("content-type", Media.PLAIN_TEXT)

        response = _Response(
            content=self._content,
            headers=self.headers,
            status_code=self.status_code,
            background=self.background_task,
        )
        await response(receive, send)
