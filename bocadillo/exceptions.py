from http import HTTPStatus
from typing import Union, Any, List


class HTTPError(Exception):
    """Raised when an HTTP error occurs.

    You can raise this within a view or an error handler to interrupt
    request processing.

    # Parameters
    status (int or HTTPStatus):
        the status code of the error.
    detail (any):
        extra detail information about the error. The exact rendering is
        determined by the configured error handler for `HTTPError`.

    # See Also
    - [HTTP response status codes (MDN web docs)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
    """

    def __init__(self, status: Union[int, HTTPStatus], detail: Any = ""):
        if isinstance(status, int):
            status = HTTPStatus(status)
        else:
            assert isinstance(
                status, HTTPStatus
            ), f"Expected int or HTTPStatus, got {type(status)}"
        self._status = status
        self.detail = detail

    @property
    def status_code(self) -> int:
        """Return the HTTP error's status code, e.g. `404`."""
        return self._status.value

    @property
    def status_phrase(self) -> str:
        """Return the HTTP error's status phrase, e.g. `"Not Found"`."""
        return self._status.phrase

    @property
    def title(self) -> str:
        """Return the HTTP error's title, e.g. `"404 Not Found"`."""
        return f"{self.status_code} {self.status_phrase}"

    def __str__(self):
        return self.title


class UnsupportedMediaType(Exception):
    """Raised when trying to use an unsupported media type.

    # Parameters
    media_type (str):
        the unsupported media type.
    available (list of str):
        a list of supported media types.
    """

    def __init__(self, media_type: str, available: List[str]):
        self._media_type = media_type
        self._available = available

    def __str__(self):
        return f'{self._media_type} (available: {", ".join(self._available)})'
