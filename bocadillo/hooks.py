from collections import defaultdict
from functools import wraps
from typing import Callable, Union, Dict, Coroutine

from .compat import call_async, asynccontextmanager
from .request import Request
from .response import Response
from .routing import Route

HookFunction = Callable[[Request, Response, dict], Coroutine]
HookCollection = Dict[Route, HookFunction]

BEFORE = "before"
AFTER = "after"


async def empty_hook(req: Request, res: Response, params: dict):
    pass


class HooksBase:
    """Base class for hooks managers.

    When subclassing:

    - `route_class` should be defined.
    - `store_hook()` should be implemented.
    """

    route_class = None

    def store_hook(self, hook: str, hook_function: HookFunction, route: Route):
        """Store a hook function for a route.

        The implementation must be defined by subclasses.

        # Parameters

        hook (str):
            The name of the hook.
        hook_function (HookFunction):
            A hook function.
        route (Route):
            A route object.
        """
        raise NotImplementedError

    def before(self, hook_function: HookFunction, *args, **kwargs):
        return self._hook_decorator(BEFORE, hook_function, *args, **kwargs)

    def after(self, hook_function: HookFunction, *args, **kwargs):
        return self._hook_decorator(AFTER, hook_function, *args, **kwargs)

    def _hook_decorator(
        self, hook: str, hook_function: HookFunction, *args, **kwargs
    ):
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
            nonlocal self, hook_function
            hook_function = _prepare_async_hook_function(
                hook_function, *args, **kwargs
            )

            if isinstance(hookable, self.route_class):
                route = hookable
                self.store_hook(hook, hook_function, route)
                return route
            else:
                return _with_hook(hookable, hook, hook_function)

        return decorator


class Hooks(HooksBase):
    """A concrete hooks manager that stores hooks by route."""

    route_class = Route

    def __init__(self):
        self._hooks: Dict[str, HookCollection] = {
            BEFORE: defaultdict(lambda: empty_hook),
            AFTER: defaultdict(lambda: empty_hook),
        }

    def store_hook(self, hook: str, hook_function: HookFunction, route: Route):
        self._hooks[hook][route] = hook_function

    @asynccontextmanager
    async def on(self, route, request, response, params):
        """Execute `before` hooks on enter and `after` hooks on exit."""
        await call_async(self._hooks[BEFORE][route], request, response, params)
        yield
        await call_async(self._hooks[AFTER][route], request, response, params)


class HooksMixin:
    """Mixin that provides hooks to application classes."""

    _hooks_manager_class = Hooks

    def __init__(self):
        super().__init__()
        self._hooks = self._hooks_manager_class()

    def get_hooks(self):
        return self._hooks

    def before(self, hook_function: HookFunction, *args, **kwargs):
        """Register a before hook on a route.

        ::: tip NOTE
        `@api.before()` should be placed  **above** `@api.route()`
        when decorating a view.
        :::

        # Parameters
        hook_function (callable):\
            A synchronous or asynchronous function with the signature:
            `(req, res, params) -> None`.
        """
        return self.get_hooks().before(hook_function, *args, **kwargs)

    def after(self, hook_function: HookFunction, *args, **kwargs):
        """Register an after hook on a route.

        ::: tip NOTE
        `@api.after()` should be placed **above** `@api.route()`
        when decorating a view.
        :::

        # Parameters
        hook_function (callable):\
            A synchronous or asynchronous function with the signature:
            `(req, res, params) -> None`.
        """
        return self.get_hooks().after(hook_function, *args, **kwargs)


def _prepare_async_hook_function(
    full_hook_function, *args, **kwargs
) -> HookFunction:
    async def hook_function(req: Request, res: Response, params: dict):
        await call_async(full_hook_function, req, res, params, *args, **kwargs)

    return hook_function


def _with_hook(view: Callable, hook: str, hook_function: HookFunction):
    @wraps(view)
    async def with_hook(self, req, res, **kw):
        if hook == BEFORE:
            await hook_function(req, res, kw)
        await call_async(view, self, req, res, **kw)
        if hook == AFTER:
            await hook_function(req, res, kw)

    return with_hook
