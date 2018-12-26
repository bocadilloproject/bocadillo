from typing import List, Union, Any, Awaitable, Callable, Dict

from bocadillo.constants import ALL_HTTP_METHODS
from .request import Request
from .response import Response

Handler = Callable[[Request, Response, Any], Awaitable[None]]


class ViewMeta(type):
    def __new__(mcs, name, bases, namespace):
        # TODO populate all methods if "handle" is defined
        # TODO populate "head" if "get" is defined
        # TODO check that declared HTTP methods are valid
        # TODO check all handlers accept at least req and res parameters
        # TODO convert handlers to async if necessary
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

    @classmethod
    def from_handler(mcs: "ViewMeta", handler: Handler, methods: List[str]):
        namespace = {method: handler for method in methods}
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


class View(ViewLike, metaclass=ViewMeta):
    """Base view class."""


def get_handlers(view: ViewLike) -> Dict[str, Handler]:
    """Get handlers declared on a view.

    # Parameters
    view (View): a `View` object.

    # Returns
    handlers (dict):
        A dict mapping an HTTP method to a handler.
    """
    return {
        method: getattr(view, method)
        for method in map(str.lower, ALL_HTTP_METHODS)
        if hasattr(view, method)
    }


def view(methods: Union[List[str], all]):
    """Convert a single function handler to a view class.

    # Parameters
    methods (list of str):
        A list of supported HTTP methods. The `all` built-in can be used
        to support all available HTTP methods.
    """
    methods = ["handle"] if methods is all else [m.lower() for m in methods]

    def decorate(handler: Handler) -> ViewMeta:
        handler = staticmethod(handler)
        return View.from_handler(staticmethod(handler), methods)

    return decorate
