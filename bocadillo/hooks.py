from functools import wraps
from typing import Callable, Dict, Coroutine

from bocadillo.routing import Route
from bocadillo.views import Handler
from .compat import call_async
from .request import Request
from .response import Response

HookFunction = Callable[[Request, Response, dict], Coroutine]
HookCollection = Dict[Route, HookFunction]

BEFORE = "before"
AFTER = "after"


async def empty_hook(req: Request, res: Response, params: dict):
    pass


class Hooks:
    """Hooks manager."""

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

    def _hook_decorator(
        self, hook_type: str, hook: HookFunction, *args, **kwargs
    ):
        def decorator(handler: Handler):
            """Bind the hook_type function to the given handler."""

            # Enclose args and kwargs
            async def hook_func(req: Request, res: Response, params: dict):
                await call_async(hook, req, res, params, *args, **kwargs)

            if hook_type == BEFORE:

                @wraps(handler)
                async def with_hook(req, res, **kw):
                    await hook_func(req, res, kw)
                    await handler(req, res, **kw)

            else:
                assert hook_type == AFTER

                @wraps(handler)
                async def with_hook(req, res, **kw):
                    await handler(req, res, **kw)
                    await hook_func(req, res, kw)

            return with_hook

        return decorator


# Pre-bind to module
hooks = Hooks()
before = hooks.before

after = hooks.after
