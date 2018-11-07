from http import HTTPStatus
from typing import Union
from jinja2.exceptions import TemplateNotFound as _TemplateNotFound

# Alias
TemplateNotFound = _TemplateNotFound


class RouteDeclarationError(Exception):
    """Raised when a route is ill-declared."""


class HTTPError(Exception):
    """Raised when an HTTP error occurs.

    You can raise this within a view or an error handler to interrupt
    request processing.
    """

    def __init__(self, status: Union[int, HTTPStatus]):
        if isinstance(status, int):
            status = HTTPStatus(status)
        else:
            assert isinstance(status, HTTPStatus), (
                f'Expected int or HTTPStatus, got {type(status)}'
            )
        self._status = status

    @property
    def http_status(self) -> HTTPStatus:
        return self._status

    @property
    def status_code(self) -> int:
        """Return the HTTP error's status code, i.e. 404."""
        return self._status.value

    @property
    def status_phrase(self) -> str:
        """Return the HTTP error's status phrase, i.e. 'Not Found'."""
        return self._status.phrase

    def __str__(self):
        return f'{self.status_code} {self.status_phrase}'