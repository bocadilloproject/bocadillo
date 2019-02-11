import inspect
from typing import (
    AnyStr,
    Any,
    Callable,
    Coroutine,
    Optional,
    AsyncIterable,
    Dict,
)

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import (
    Response as _Response,
    StreamingResponse as _StreamingResponse,
)

from .media import Media

BackgroundFunc = Callable[..., Coroutine]
StreamFunc = Callable[[], AsyncIterable[AnyStr]]


class Response:
    """Response builder."""

    CONTENT_ATTRS = {
        "text": Media.PLAIN_TEXT,
        "html": Media.HTML,
        "media": None,
    }

    def __init__(self, request: Request, media: Media):
        self.request = request
        self._content: Optional[AnyStr] = None
        self.status_code: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self._media = media
        self._background: Optional[BackgroundFunc] = None
        self._generator: Optional[AsyncIterable[bytes]] = None
        self.chunked = False

    @property
    def content(self) -> Optional[AnyStr]:
        return self._content

    @content.setter
    def content(self, content: AnyStr):
        self._content = content

    def _set_media(self, value: Any, media_type: str):
        content = self._media.serialize(value, media_type=media_type)
        self.headers["content-type"] = media_type
        self._content = content

    def __setattr__(self, key, value):
        if key in self.CONTENT_ATTRS:
            media_type = self.CONTENT_ATTRS[key] or self._media.type
            self._set_media(value, media_type=media_type)
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

    def stream(self, func: StreamFunc):
        """Stream the response.

        Should be used to decorate a no-argument asynchronous generator
        function.
        """
        assert inspect.isasyncgenfunction(func)
        self._generator = func()
        return func

    async def __call__(self, receive, send):
        """Build and send the response."""
        if self.status_code is None:
            self.status_code = 200

        if self.status_code != 204:
            self.headers.setdefault("content-type", Media.PLAIN_TEXT)

        if self.chunked:
            self.headers["transfer-encoding"] = "chunked"

        if self._generator is not None:
            response_cls = _StreamingResponse
            content = self._generator
        else:
            response_cls = _Response
            content = self.content

        response = response_cls(
            content=content,
            headers=self.headers,
            status_code=self.status_code,
            background=self.background_task,
        )
        await response(receive, send)
