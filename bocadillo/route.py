import inspect
from http import HTTPStatus
from typing import Optional, List

from asgiref.sync import sync_to_async
from parse import parse

from bocadillo.hooks import HookFunction
from .exceptions import HTTPError
from .view import View, CallableView


class Route:
    """Represents a route to a view.

    Formatted string syntax is used for route patterns.
    """

    def __init__(self,
                 pattern: str,
                 view: View,
                 methods: List[str],
                 name: str):
        self._pattern = pattern
        self._view_is_class = inspect.isclass(view)

        if self._view_is_class:
            view = view()
        elif not inspect.iscoroutinefunction(view):
            view = sync_to_async(view)

        self._view = view
        self._methods = methods
        self._name = name

        self.before = None
        self.after = None

    def url(self, **kwargs) -> str:
        """Return full path for the given route parameters."""
        return self._pattern.format(**kwargs)

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

    @classmethod
    def before_hook(cls, hook_function: HookFunction, *args):
        return cls._add_hook('before', hook_function, *args)

    @classmethod
    def after_hook(cls, hook_function: HookFunction, *args):
        return cls._add_hook('after', hook_function, *args)

    @staticmethod
    def _add_hook(hook: str, hook_function: HookFunction, *args):
        def decorator(route):
            nonlocal hook_function
            if args:
                full_hook_function = hook_function

                def hook_function(req, res, view, params):
                    return full_hook_function(req, res, view, params, *args)

            setattr(route, hook, hook_function)
            return route

        return decorator

    def _find_view(self, request) -> CallableView:
        """Find a view able to handle the request.

        Supports both function-based views and class-based views.
        """
        not_allowed_error = HTTPError(status=HTTPStatus.METHOD_NOT_ALLOWED)

        if self._view_is_class:
            if hasattr(self._view, 'handle'):
                view: CallableView = self._view.handle
            else:
                method_func_name = request.method.lower()
                view: CallableView = getattr(self._view, method_func_name, None)
                if view is None:
                    raise not_allowed_error
            if not inspect.iscoroutinefunction(view):
                view = sync_to_async(view)
        else:
            if request.method not in self._methods:
                raise not_allowed_error
            view = self._view

        return view

    async def __call__(self, request, response, **kwargs) -> None:
        view = self._find_view(request)

        if self.before is not None:
            self.before(request, response, view, kwargs)

        await view(request, response, **kwargs)

        if self.after is not None:
            self.after(request, response, view, kwargs)
