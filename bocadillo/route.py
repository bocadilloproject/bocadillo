from typing import Optional, List

from parse import parse

from .hooks import HookFunction
from .view import View, create_callable_view


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

        self._view = create_callable_view(view=view, methods=methods)
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

    async def __call__(self, request, response, **kwargs) -> None:
        view = self._view
        if self.before is not None:
            self.before(request, response, view, kwargs)
        await view(request, response, **kwargs)
        if self.after is not None:
            self.after(request, response, view, kwargs)
