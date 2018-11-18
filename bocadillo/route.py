from collections import defaultdict
from functools import wraps
from typing import Optional, List, Union, Callable, Dict

from parse import parse

from .hooks import HookFunction, BEFORE, AFTER, empty_hook
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

        self.hooks: Dict[str, HookFunction] = defaultdict(lambda: empty_hook)

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
        return cls._add_hook(BEFORE, hook_function, *args)

    @classmethod
    def after_hook(cls, hook_function: HookFunction, *args):
        return cls._add_hook(AFTER, hook_function, *args)

    @staticmethod
    def _add_hook(hook: str, hook_function: HookFunction, *args):
        def decorator(hookable: Union[Route, Callable]):
            """Bind the hook function to the given hookable object.

            Support for decorating a route or a class method enables
            using hooks in the following contexts:
            - On a function-based view (before @api.route()).
            - On top of a class-based view (before @api.route()).
            - On a class-based view method.

            Parameters
            ----------
            hookable : Route or (unbound) class method
            """
            nonlocal hook_function
            if args:
                full_hook_function = hook_function

                def hook_function(req, res, view, params):
                    return full_hook_function(req, res, view, params, *args)

            if isinstance(hookable, Route):
                route = hookable
                route.hooks[hook] = hook_function
                return route
            else:
                unbound_method_view = hookable

                @wraps(unbound_method_view)
                async def with_hook(self, req, res, **kwargs):
                    if hook == BEFORE:
                        hook_function(req, res, unbound_method_view, kwargs)
                    await unbound_method_view(self, req, res, **kwargs)
                    if hook == AFTER:
                        hook_function(req, res, unbound_method_view, kwargs)

                return with_hook

        return decorator

    async def __call__(self, request, response, **kwargs) -> None:
        view = self._view
        self.hooks[BEFORE](request, response, view, kwargs)
        await view(request, response, **kwargs)
        self.hooks[AFTER](request, response, view, kwargs)
