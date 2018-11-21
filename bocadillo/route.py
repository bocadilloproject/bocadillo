from collections import defaultdict
from functools import wraps
from typing import Optional, List, Union, Callable, Dict

from parse import parse

from .compat import call_async
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
    def before_hook(cls, hook_function: HookFunction, *args, **kwargs):
        return cls._add_hook(BEFORE, hook_function, *args, **kwargs)

    @classmethod
    def after_hook(cls, hook_function: HookFunction, *args, **kwargs):
        return cls._add_hook(AFTER, hook_function, *args, **kwargs)

    @staticmethod
    def _add_hook(hook: str, hook_function: HookFunction, *args, **kwargs):
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
            full_hook_function = hook_function

            async def hook_function(req, res, params):
                return await call_async(full_hook_function,
                                        req, res, params, *args, **kwargs)

            if isinstance(hookable, Route):
                route = hookable
                route.hooks[hook] = hook_function
                return route
            else:
                view: Callable = hookable

                @wraps(view)
                async def with_hook(self, req, res, **kwargs):
                    if hook == BEFORE:
                        await hook_function(req, res, kwargs)
                    await call_async(view, self, req, res, **kwargs)
                    if hook == AFTER:
                        await hook_function(req, res, kwargs)

                return with_hook

        return decorator

    async def __call__(self, request, response, **kwargs) -> None:
        view = self._view
        await call_async(self.hooks[BEFORE], request, response, kwargs)
        await view(request, response, **kwargs)
        await call_async(self.hooks[AFTER], request, response, kwargs)
