import inspect
from functools import partial, wraps
from typing import List, Union, Any, Awaitable, Callable, Dict

from .compat import call_async
from .constants import ALL_HTTP_METHODS
from .request import Request
from .response import Response

Handler = Callable[[Request, Response, Any], Awaitable[None]]


class View:
    """View type."""

    def __init__(self, name: str):
        self.name = name

    get: Handler
    post: Handler
    put: Handler
    patch: Handler
    delete: Handler
    head: Handler
    options: Handler

    @classmethod
    def _create(cls, name: str, docstring: str, handlers: dict) -> "View":
        view = cls(name)
        view.__doc__ = docstring

        # Convert handlers to async if necessary
        for method, handler in handlers.items():
            if not inspect.iscoroutinefunction(handler):
                handler = wraps(handler)(partial(call_async, handler))
                handlers[method] = handler

        # Set head handler if not given but get is given.
        if "get" in handlers and "head" not in handlers:
            handlers["head"] = handlers["get"]

        # If catch-all "handle" handler is given, override all other handlers.
        if "handle" in handlers:
            for method in map(str.lower, ALL_HTTP_METHODS):
                handlers[method] = handlers["handle"]

        for method, handler in handlers.items():
            setattr(view, method, handler)

        return view

    @classmethod
    def from_handler(cls, handler: Handler, methods: List[str]) -> "View":
        handlers = {method: handler for method in methods}
        return cls._create(handler.__name__, handler.__doc__, handlers)

    @classmethod
    def from_obj(cls, obj: Any) -> "View":
        handlers = get_handlers(obj)
        return cls._create(obj.__class__.__name__, obj.__doc__, handlers)


def get_handlers(view: View) -> Dict[str, Handler]:
    """Get handlers declared on a view or a view-like dictionary.

    # Parameters
    view (View): a view-like object.

    # Returns
    handlers (dict):
        A dict mapping an HTTP method to a handler.
    """
    return {
        method: getattr(view, method)
        for method in ("handle", *map(str.lower, ALL_HTTP_METHODS))
        if hasattr(view, method)
    }


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
        methods = ["handle"]
    else:
        methods = [m.lower() for m in methods]

    return partial(View.from_handler, methods=methods)
