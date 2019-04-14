from starlette.responses import RedirectResponse


class Redirect(Exception):
    """Raise when redirecting to another page."""

    __slots__ = ("_url", "_permanent")

    def __init__(self, url: str, permanent: bool = False):
        super().__init__()
        self._url = url
        self._permanent = permanent

    @property
    def status_code(self) -> int:
        return 301 if self._permanent else 302

    @property
    def response(self) -> RedirectResponse:
        return RedirectResponse(url=self._url, status_code=self.status_code)
