from starlette.responses import RedirectResponse


class Redirection(Exception):
    """Raised when redirecting to another page."""

    def __init__(self, url: str, permanent: bool):
        self._url = url
        self._permanent = permanent

    @property
    def status_code(self) -> int:
        return 301 if self._permanent else 302

    @property
    def response(self) -> RedirectResponse:
        return RedirectResponse(url=self._url, status_code=self.status_code)
