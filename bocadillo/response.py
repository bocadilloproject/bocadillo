import inspect
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Coroutine,
    Dict,
    Optional,
    Union,
)

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import (
    Response as _Response,
    StreamingResponse as _StreamingResponse,
)

from .media import Media

AnyStr = Union[str, bytes]
BackgroundFunc = Callable[..., Coroutine]
Stream = AsyncIterable[AnyStr]
StreamFunc = Callable[[], Stream]


class Response:
    """The response builder, passed to HTTP views and typically named `res`.

    At the lower-level, `Response` behaves like an ASGI application instance:
    it is a callable and accepts `receive` and `send` as defined in the [ASGI
    spec](https://asgi.readthedocs.io/en/latest/specs/main.html#applications).

    [media]: ../guides/http/media.md

    # Attributes
    content (bytes or str): the raw response content.
    status_code (int): the HTTP status code. If not set, defaults to `200`.
    headers (dict):
        a case-insensitive dictionary of HTTP headers.
        If not set, `content-type` header is set to `text/plain`.
    request (Request): the currently processed request.
    chunked (bool): sets the `transfer-encoding` header to `chunked`.

    **Content setters**

    These write-only properties set the response's `content`.

    text (str): uses the `text/plain` content type.
    html (str): uses the `text/html` content type.
    media (any): uses the configured [media] handler.

    """

    _MEDIA_ATTRS = {"text": Media.PLAIN_TEXT, "html": Media.HTML, "media": None}

    def __init__(self, request: Request, media: Media):
        # Public attributes.
        self.content: Optional[AnyStr] = None
        self.request = request
        self.status_code: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self.chunked = False
        # Private attributes.
        self._media = media
        self._background: Optional[BackgroundFunc] = None
        self._stream: Optional[Stream] = None

    def _set_media(self, value: Any, media_type: str):
        content = self._media.serialize(value, media_type=media_type)
        self.headers["content-type"] = media_type
        self.content = content

    def __setattr__(self, key, value):
        if key in self._MEDIA_ATTRS:
            media_type = self._MEDIA_ATTRS[key] or self._media.type
            self._set_media(value, media_type=media_type)
        else:
            super().__setattr__(key, value)

    def background(
        self, func: BackgroundFunc, *args, **kwargs
    ) -> BackgroundFunc:
        """Register a coroutine function to be executed in the background.

        This can be used either as a decorator or a regular function.

        # Parameters
        func (callable):
            A coroutine function.
        *args, **kwargs:
            Any positional and keyword arguments to pass to `func` when
            executing it.
        """

        async def background():
            await func(*args, **kwargs)

        self._background = background
        return func

    @property
    def _background_task(self) -> Optional[BackgroundTask]:
        if self._background is not None:
            return BackgroundTask(self._background)
        return None

    def stream(self, func: StreamFunc) -> StreamFunc:
        """Stream the response.

        Should be used to decorate a no-argument asynchronous generator
        function.
        """
        assert inspect.isasyncgenfunction(func)
        self._stream = func()
        return func

    async def __call__(self, receive, send):
        """Build and send the response."""
        if self.status_code is None:
            self.status_code = 200

        if self.status_code != 204:
            self.headers.setdefault("content-type", Media.PLAIN_TEXT)

        if self.chunked:
            self.headers["transfer-encoding"] = "chunked"

        response_kwargs = {
            "content": self.content,
            "status_code": self.status_code,
            "headers": self.headers,
            "background": self._background_task,
        }

        response_cls = _Response

        if self._stream is not None:
            response_cls = _StreamingResponse
            response_kwargs["content"] = self._stream

        response: _Response = response_cls(**response_kwargs)
        await response(receive, send)
