import inspect
from typing import AnyStr, Callable, Optional, Union, Type

from parse import parse

from bocadillo.utils import _ensure_async
from .request import Request
from .response import Response
from .view import BaseView


View = Union[Callable[[Request, Response, dict], None], Type[BaseView]]


class Route:
    """Represents a route to a view.

    Formatted string syntax is used for route patterns.
    """

    def __init__(self, pattern: AnyStr, view: View):
        self._pattern = pattern
        self._view_is_class = inspect.isclass(view)
        if self._view_is_class:
            view = view()
        self._view = view

    def match(self, path: str) -> Optional[dict]:
        """Return whether the route matches the given path.

        Examples
        -------
        >>> route = Route('/{age:d}', lambda req, resp: None)
        >>> route.match('/42')
        {'age': 42}
        >>> route.match('/john')
        None
        """
        result = parse(self._pattern, path)
        return result is not None and result.named or None

    def _find_view(self, request):
        """Find a view able to handle the request.

        Supports both function-based views and class-based views.
        """
        if self._view_is_class:
            handler = getattr(self._view, request.method.lower(), None)
            if handler is None:
                # TODO use MethodNotAllowed exception
                raise ValueError('Method not allowed', request.method)
        else:
            handler = self._view
        return handler

    async def __call__(self, request, response, **kwargs):
        view = self._find_view(request)
        await _ensure_async(view, request, response, **kwargs)
