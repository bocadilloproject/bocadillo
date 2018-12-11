import asyncio
import inspect
from typing import Callable, Union, Coroutine

from .compat import call_async
from .constants import ALL_HTTP_METHODS
from .request import Request
from .response import Response


class ClassBasedView:
    """Class-based view interface."""

    def get(self, req: Request, res: Response, **kwargs):
        raise NotImplementedError

    def post(self, req: Request, res: Response, **kwargs):
        raise NotImplementedError

    def put(self, req: Request, res: Response, **kwargs):
        raise NotImplementedError

    def patch(self, req: Request, res: Response, **kwargs):
        raise NotImplementedError

    def delete(self, req: Request, res: Response, **kwargs):
        raise NotImplementedError

    def head(self, req: Request, res: Response, **kwargs):
        raise NotImplementedError

    def options(self, req: Request, res: Response, **kwargs):
        raise NotImplementedError


# Types
AsyncView = Callable[[Request, Response, dict], Coroutine]
View = Union[AsyncView, ClassBasedView]


def create_async_view(view: View) -> AsyncView:
    """Create function asynchronous view from function or class-based view."""
    if asyncio.iscoroutinefunction(view):
        return view
    elif inspect.isfunction(view):

        async def callable_view(req, res, **kwargs):
            await call_async(view, req, res, sync=True, **kwargs)

        return callable_view
    else:
        return _from_class_instance(view)


def _from_class_instance(view: ClassBasedView):
    def _find_for_method(method: str):
        try:
            return getattr(view, "handle")
        except AttributeError:
            return getattr(view, method.lower())

    async def callable_view(req, res, **kwargs):
        view_ = _find_for_method(req.method)
        await call_async(view_, req, res, **kwargs)

    return callable_view


def get_view_name(view: View, base: ClassBasedView = None) -> str:
    def _get_name(obj):
        return getattr(obj, "__name__", obj.__class__.__name__)

    return ".".join(_get_name(part) for part in (base, view) if part)


def get_declared_method_views(view: ClassBasedView):
    for method in ("handle", *map(str.lower, ALL_HTTP_METHODS)):
        if hasattr(view, method):
            yield method, getattr(view, method)
