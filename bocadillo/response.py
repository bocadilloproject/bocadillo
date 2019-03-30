from functools import partial
from os.path import basename
from typing import Any, Callable, Coroutine, Dict, Optional, Union

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import FileResponse as _FileResponse
from starlette.responses import Response as _Response
from starlette.responses import StreamingResponse as _StreamingResponse

from .constants import CONTENT_TYPE
from .media import MediaHandler
from .streaming import Stream, StreamFunc, stream_until_disconnect

AnyStr = Union[str, bytes]
BackgroundFunc = Callable[..., Coroutine]


def _content_setter(content_type: str):
    def fset(res: "Response", value: AnyStr):
        res.content = value
        res.headers["content-type"] = content_type

    doc = (
        "Write-only property that sets `content` to the set value and sets "
        f'the `Content-Type` header to `"{content_type}"`.'
    )

    return property(fget=None, fset=fset, doc=doc)


class Response:
    """The response builder, passed to HTTP views and typically named `res`.

    At the lower-level, `Response` behaves like an ASGI application instance:
    it is a callable and accepts `receive` and `send` as defined in the [ASGI
    spec](https://asgi.readthedocs.io/en/latest/specs/main.html#applications).

    [media]: ../guides/http/media.md
    [Content-Disposition]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition

    # Parameters
    request:
        the currently processed #::bocadillo.request#Request.
    media_type (str):
        the configured media type (given by the #::bocadillo.applications#App).
    media_handler (callable):
        the configured media handler
        (given by the #::bocadillo.applications#App).

    # Attributes
    content (bytes or str): the raw response content.
    status_code (int): the HTTP status code. If not set, defaults to `200`.
    headers (dict):
        a case-insensitive dictionary of HTTP headers.
        If not set, `content-type` header is set to `text/plain`.
    chunked (bool): sets the `transfer-encoding` header to `chunked`.
    attachment (str):
        a file name that this response should be sent as.
        This is done by setting the [Content-Disposition] header, and
        typically makes the client browser trigger a "Save As…" dialog or
        download and save the file locally.
    """

    __slots__ = (
        "content",
        "request",
        "status_code",
        "headers",
        "chunked",
        "attachment",
        "_file_path",
        "_media_type",
        "_media_handler",
        "_background",
        "_stream",
    )

    text = _content_setter(CONTENT_TYPE.PLAIN_TEXT)
    html = _content_setter(CONTENT_TYPE.HTML)

    def __init__(
        self, request: Request, media_type: str, media_handler: MediaHandler
    ):
        # Public attributes.
        self.content: Optional[AnyStr] = None
        self.request = request
        self.status_code: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self.chunked = False
        self.attachment: Optional[str] = None
        # Private attributes.
        self._file_path: Optional[str] = None
        self._media_type = media_type
        self._media_handler = media_handler
        self._background: Optional[BackgroundFunc] = None
        self._stream: Optional[Stream] = None

    media = property(
        doc=(
            "Write-only property that sets `content` to the set value "
            "serialized using the `media_handler`, and sets the "
            "`Content-Type` header to the `media_type`."
        )
    )

    @media.setter
    def media(self, value: Any):
        self.content = self._media_handler(value)
        self.headers["content-type"] = self._media_type

    def file(self, path: str, attach: bool = True):
        """Send a file asynchronously using [aiofiles].

        [aiofiles]: https://github.com/Tinche/aiofiles

        # Parameters
        path (str):
            a path to a file on this machine.
        attach (bool, optional):
            whether to send the file as an [attachment](#response).
            Defaults to `True`.
        """
        self._file_path = path
        if attach:
            self.attachment = basename(path)

    def background(
        self, func: BackgroundFunc, *args, **kwargs
    ) -> BackgroundFunc:
        """Register a coroutine function to be executed in the background.

        This can be used either as a decorator or a regular function.

        # Parameters
        func (callable):
            a coroutine function.
        *args, **kwargs:
            any positional and keyword arguments to pass to `func` when
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

    def stream(
        self, func: StreamFunc = None, raise_on_disconnect: bool = False
    ) -> StreamFunc:
        """Stream the response.

        The decorated function should be a no-argument asynchronous generator
        function that yields chunks of the response (strings or bytes).

        If `raise_on_disconnect` is `True`,  a `ClientDisconnect` exception
        is raised in the generator when it `yield`s a chunk but the client
        has disconnected. Otherwise, the exception is handled and the stream
        stops.
        """
        if func is None:
            return partial(self.stream, raise_on_disconnect=raise_on_disconnect)

        self._stream = stream_until_disconnect(
            self.request, func(), raise_on_disconnect=raise_on_disconnect
        )

        return func

    def event_stream(self, func: StreamFunc = None, **kwargs) -> StreamFunc:
        """Stream server-sent events.

        The decorated function should be a no-argument asynchronous generator
        function that yields SSE messages (strings or bytes).
        You can use the [server_event](./sse.md#server-event) helper to
        ensure that messages are correctly formatted.

        This is nearly equivalent to `@stream()`. The only difference is that
        this decorator also sets SSE-specific HTTP headers:

        - `Cache-Control: no-cache`
        - `Content-Type: text/event-stream`
        - `Connection: Keep-Alive`

        # See Also
        - [Using server-sent events (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
        """
        self.headers = {
            "cache-control": "no-cache",
            **self.headers,
            "content-type": "text/event-stream",
            "connection": "keep-alive",
        }
        return self.stream(func, **kwargs)

    async def __call__(self, receive, send):
        """Build and send the response."""
        if self.status_code is None:
            self.status_code = 200

        if self.status_code != 204:
            self.headers.setdefault("content-type", "text/plain")

        if self.chunked:
            self.headers["transfer-encoding"] = "chunked"

        if self.attachment is not None:
            disposition = f"attachment; filename='{self.attachment}'"
            self.headers.setdefault("content-disposition", disposition)

        response_kwargs = {
            "content": self.content,
            "headers": self.headers,
            "status_code": self.status_code,
            "background": self._background_task,
        }

        response_cls = _Response

        if self._file_path is not None:
            response_cls = _FileResponse
            response_kwargs["path"] = self._file_path
            # `FileResponse` will populate the response from `path` and
            # doesn't expect `content` to be passed.
            del response_kwargs["content"]
            # `FileResponse` will set the status code to 200.
            del response_kwargs["status_code"]
        elif self._stream is not None:
            response_cls = _StreamingResponse
            response_kwargs["content"] = self._stream

        response: _Response = response_cls(**response_kwargs)
        await response(receive, send)
