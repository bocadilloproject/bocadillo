import inspect
from os.path import basename
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
    FileResponse as _FileResponse,
)

from .media import Media

try:
    import aiofiles
except ImportError:
    aiofiles = None

AnyStr = Union[str, bytes]

BackgroundFunc = Callable[..., Coroutine]
Stream = AsyncIterable[AnyStr]
StreamFunc = Callable[[], Stream]


class Response:
    """Response builder."""

    _MEDIA_ATTRS = {"text": Media.PLAIN_TEXT, "html": Media.HTML, "media": None}

    def __init__(self, request: Request, media: Media):
        # Public attributes.
        self.request = request
        self.status_code: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self.chunked = False
        # Private attributes.
        self._content: Optional[AnyStr] = None
        self._media = media
        self._background: Optional[BackgroundFunc] = None
        self._stream: Optional[Stream] = None
        self._file_path: Optional[str] = None

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
        if key in self._MEDIA_ATTRS:
            media_type = self._MEDIA_ATTRS[key] or self._media.type
            self._set_media(value, media_type=media_type)
        else:
            super().__setattr__(key, value)

    def attach(
        self, path: str = None, content: str = None, inline: bool = False
    ):
        """Send a file for the client to download.

        The [Content-Disposition] header is set automatically based on the
        `inline` argument.

        [Content-Disposition]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition

        # Parameters
        path (str, optional):
            A path to a file on this machine.
        content (str, optional):
            Raw content to be sent, instead of reading from a file.
        filename (str, optional):
            The name of the file to be sent.
            If `path` is given, its base name (as given by `os.path.basename`)
            is used. Otherwise, this is a required parameter.
        inline (bool, optional):
            Whether the file should be sent `inline` (for in-browser preview)
            or as an `attachment` (typically triggers a "Save As" dialog).
            Defaults to `False`, i.e. send as an attachment.
        """
        if path is not None:
            self._file_path = path
            filename = basename(path)
        else:
            assert (
                content is not None
            ), "`content` is required if `path` is not given"
            assert (
                filename is not None
            ), "`filename` is required if `path` is not given"
            self._content = content

        disposition = "inline" if inline else "attachment"
        content_disposition = f"{disposition}; filename='{filename}'"
        self.headers.setdefault("content-disposition", content_disposition)

    def background(self, func: BackgroundFunc, *args, **kwargs):
        """Register a coroutine function to be executed in the background."""

        async def background():
            await func(*args, **kwargs)

        self._background = background
        return func

    @property
    def _background_task(self) -> Optional[BackgroundTask]:
        if self._background is not None:
            return BackgroundTask(self._background)
        return None

    def stream(self, func: StreamFunc):
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

        res_kwargs = {
            "content": self.content,
            "headers": self.headers,
            "status_code": self.status_code,
            "background": self._background_task,
        }

        res_cls = _Response

        if self._file_path is not None:
            res_cls = _FileResponse
        elif self._stream is not None:
            res_cls = _StreamingResponse
            res_kwargs["content"] = self._stream

        response = res_cls(**res_kwargs)
        await response(receive, send)
