import inspect
from functools import wraps
import typing

from .compat import check_async
from .request import Request
from .response import Response
from .routing import HTTPRoute
from .views import Handler, get_handlers, View

HookFunction = typing.Callable[
    [Request, Response, dict], typing.Awaitable[None]
]
HookCollection = typing.Dict[HTTPRoute, HookFunction]

BEFORE = "before"
AFTER = "after"


class Hooks:
    """Hooks manager."""

    __slots__ = ()

    def before(self, hook: HookFunction, *args, **kwargs):
        """Register a before hook on a handler.

        # Parameters
        hook (callable): a hook function.
        """
        return self._hook_decorator(BEFORE, hook, *args, **kwargs)

    def after(self, hook: HookFunction, *args, **kwargs):
        """Register an after hook on a handler.

        # Parameters
        hook (callable): a hook function.
        """
        return self._hook_decorator(AFTER, hook, *args, **kwargs)

    @staticmethod
    def _prepare(hook, *args, **kwargs) -> HookFunction:
        class_based = not inspect.isfunction(hook)

        if class_based:
            assert hasattr(
                hook, "__call__"
            ), "class-based hooks must implement __call__()"

        check_target = hook.__call__ if class_based else hook
        name = (
            hook.__class__.__name__ + ".__call__"
            if class_based
            else hook.__name__
        )
        check_async(check_target, reason=f"hook '{name}' must be asynchronous")

        # Enclose args and kwargs
        async def hook_func(req: Request, res: Response, params: dict):
            await hook(req, res, params, *args, **kwargs)

        return hook_func

    def _hook_decorator(
        self, hook_type: str, hook: HookFunction, *args, **kwargs
    ):
        hook = self._prepare(hook, *args, **kwargs)

        def attach_hook(handler: typing.Union[typing.Type[View], Handler]):
            if inspect.isclass(handler):
                # Recursively apply the hook to all handlers.
                for method, _handler in get_handlers(handler).items():
                    setattr(handler, method, attach_hook(_handler))
                return handler
            return _with_hook(hook_type, hook, handler)

        return attach_hook


def _with_hook(hook_type: str, func: HookFunction, handler: Handler):
    async def call_hook(args, kw):
        if len(args) == 2:
            req, res = args
        else:
            # method that has `self` as a first parameter
            req, res = args[1:3]
        assert isinstance(req, Request)
        assert isinstance(res, Response)
        await func(req, res, kw)

    if hook_type == BEFORE:

        @wraps(handler)
        async def with_before_hook(*args, **kwargs):
            await call_hook(args, kwargs)
            await handler(*args, **kwargs)

        return with_before_hook

    assert hook_type == AFTER

    @wraps(handler)
    async def with_after_hook(*args, **kwargs):
        await handler(*args, **kwargs)
        await call_hook(args, kwargs)

    return with_after_hook


# Pre-bind to module
_HOOKS = Hooks()
before = _HOOKS.before
after = _HOOKS.after
