from contextlib import contextmanager
from typing import Optional

from aiodine import Store, scopes

from .compat import nullcontext
from .request import Request
from .response import Response

# pylint: disable=invalid-name
_STORE = Store(
    scope_aliases={"request": scopes.FUNCTION, "app": scopes.SESSION},
    providers_module="providerconf",
    default_scope=scopes.FUNCTION,
)
provider = _STORE.provider
discover_providers = _STORE.discover
useprovider = _STORE.useprovider
consumer = _STORE.consumer
freeze_providers = _STORE.freeze


class AppProvidersMixin:
    """Utility mixin for application-level providers."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._response: Optional[Response] = None
        self._request: Optional[Request] = None

        @provider
        async def req():
            return self._request

        @provider
        async def res():
            return self._response

        self._frozen = False

    def app_providers(self):  # pylint: disable=method-hidden
        if not self._frozen:
            freeze_providers()
            self._frozen = True
            # do nothing on subsequent calls
            self.app_providers = nullcontext
        return nullcontext()

    @contextmanager
    def provide_req(self, req: Request):
        self._request = req
        try:
            yield
        finally:
            self._request = None

    @contextmanager
    def provide_res(self, res: Response):
        self._response = res
        try:
            yield
        finally:
            self._response = None
