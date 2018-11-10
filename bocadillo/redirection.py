from starlette.responses import RedirectResponse


class Redirection(Exception):
    """Raised when redirecting to another page."""

    def __init__(self, url: str):
        self._response = RedirectResponse(url=url)

    @property
    def response(self) -> RedirectResponse:
        return self._response
