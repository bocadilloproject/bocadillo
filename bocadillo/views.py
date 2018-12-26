import inspect
from functools import partial, wraps
from typing import List, Union, Any, Awaitable, Callable, Dict

from bocadillo.compat import call_async
from bocadillo.constants import ALL_HTTP_METHODS
from .request import Request
from .response import Response

Handler = Callable[[Request, Response, Any], Awaitable[None]]


class ViewMeta(type):
    def __new__(mcs, name, bases, namespace):
        # TODO check that declared HTTP methods are valid
        # TODO check all handlers accept at least req and res parameters

        cls: "ViewMeta" = super().__new__(mcs, name, bases, namespace)

        # Convert handlers to async if necessary
        for method, handler in get_handlers(cls()).items():
            if not inspect.iscoroutinefunction(handler):
                handler = wraps(handler)(partial(call_async, handler))
                setattr(cls, method, handler)

        # Set head handler if not implemented but get is implemented.
        if hasattr(cls, "get") and not hasattr(cls, "head"):
            cls.head = cls.get

        # If catch-all "handle" handler is implemented, override all other
        # handlers.
        if hasattr(cls, "handle"):
            for method in map(str.lower, ALL_HTTP_METHODS):
                setattr(cls, method, cls.handle)
        return cls

    @classmethod
    def from_handler(mcs: "ViewMeta", handler: Handler, methods: List[str]):
        if "get" in methods and "head" not in methods:
            methods.append("head")
        # Wrap handler in `staticmethod()` to ignore `self` parameter.
        namespace = {method: staticmethod(handler) for method in methods}
        cls = mcs(handler.__name__, (), namespace)
        cls.__doc__ = handler.__doc__
        return cls

    @classmethod
    def from_view_like(mcs: "ViewMeta", obj: "ViewLike"):
        namespace = get_handlers(obj)
        cls = mcs(obj.__class__.__name__, (), namespace)
        cls.__doc__ = obj.__doc__
        return cls


class ViewLike:
    """What a view looks like."""

    get: Handler
    post: Handler
    put: Handler
    patch: Handler
    delete: Handler
    head: Handler
    options: Handler


def get_handlers(view: Union[ViewLike, dict]) -> Dict[str, Handler]:
    """Get handlers declared on a view or a view-like dictionary.

    # Parameters
    view (View or dict): a view-like object.

    # Returns
    handlers (dict):
        A dict mapping an HTTP method to a handler.
    """
    methods = ("handle", *map(str.lower, ALL_HTTP_METHODS))
    if isinstance(view, dict):
        return {
            method: view.get(method) for method in methods if method in view
        }
    else:
        return {
            method: getattr(view, method)
            for method in methods
            if hasattr(view, method)
        }


class View(ViewLike, metaclass=ViewMeta):
    """Base view class."""


def view(methods: Union[List[str], all] = None):
    """Convert a single function handler to a view class.

    # Parameters
    methods (list of str):
        A list of supported HTTP methods. The `all` built-in can be used
        to support all available HTTP methods.
        Defaults to `["get"]`.
    """
    if methods is None:
        methods = ["get"]
    if methods is all:
        methods = ALL_HTTP_METHODS
    methods = [m.lower() for m in methods]

    def decorate(handler: Handler) -> ViewMeta:
        return View.from_handler(handler, methods)

    return decorate
