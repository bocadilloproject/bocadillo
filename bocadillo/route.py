import inspect
from typing import AnyStr, Callable, Optional, Union, Type

from asgiref.sync import sync_to_async
from parse import parse

from .request import Request
from .response import Response
from .view import BaseView


CallableView = Callable[[Request, Response, dict], None]
ClassView = Type[BaseView]
View = Union[CallableView, ClassView]


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
        if result is not None:
            return result.named
        return None

    def _find_view(self, request) -> CallableView:
        """Find a view able to handle the request.

        Supports both function-based views and class-based views.
        """
        if self._view_is_class:
            if hasattr(self._view, 'handle'):
                view = self._view.handle
            else:
                view = getattr(self._view, request.method.lower(), None)
                if view is None:
                    # TODO use MethodNotAllowed exception
                    raise ValueError('Method not allowed', request.method)
        else:
            view = self._view
        return view

    async def __call__(self, request, response, **kwargs):
        view = self._find_view(request)
        if not inspect.iscoroutinefunction(view):
            view = sync_to_async(view)
        await view(request, response, **kwargs)
