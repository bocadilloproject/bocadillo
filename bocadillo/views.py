import inspect
from functools import partial, wraps
from typing import Any, Dict, List, Optional, Union

from .app_types import Handler
from .compat import call_async, camel_to_snake
from .constants import ALL_HTTP_METHODS

MethodsParam = Union[List[str], all]


class HandlerDoesNotExist(Exception):
    # Raised to signal that no handler exists for a requested HTTP method.
    pass


class View:
    """This class defines how all HTTP views are represented internally.

    ::: warning
    Views objects should not be created directly. Instead, use
    [from_handler](#from-handler) or [from_obj](#from-obj).
    :::

    HTTP methods are mapped to **handlers**, i.e. methods of a `View` object.

    The following handlers are supported:

    - `.get(req, res, **kwargs)`
    - `.post(req, res, **kwargs)`
    - `.put(req, res, **kwargs)`
    - `.patch(req, res, **kwargs)`
    - `.delete(req, res, **kwargs)`
    - `.head(req, res, **kwargs)`
    - `.options(req, res, **kwargs)`
    - `.handle(req, res, **kwargs)`

    ::: tip
    `.handle()` is special: if defined, it overrides all others.
    :::

    # Attributes

    name (str): the name of the view.
    """

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
    def create(cls, name: str, docstring: str, handlers: dict) -> "View":
        # Convert handlers to async if necessary
        for method, handler in handlers.items():
            if not inspect.iscoroutinefunction(handler):
                handler = wraps(handler)(partial(call_async, handler))
                handlers[method] = handler

        # Set head handler if not given but get is given.
        if "get" in handlers and "head" not in handlers:
            handlers["head"] = handlers["get"]

        # Create the view object.
        vue = cls(name)
        vue.__doc__ = docstring

        # Assign method handlers.
        for method, handler in handlers.items():
            setattr(vue, method, handler)

        return vue

    def get_handler(self, method: str) -> Handler:
        try:
            return getattr(self, "handle")
        except AttributeError:
            try:
                return getattr(self, method)
            except AttributeError as exc:
                raise HandlerDoesNotExist from exc


def from_handler(handler: Handler, methods: MethodsParam = None) -> View:
    """Convert a handler to a `View` instance.

    # Parameters
    handler (function or coroutine function):
        Its name and docstring are copied onto the view.
        It used as a handler for each of the declared `methods`.
        For example, if `methods=["post"]` then the returned `view` object
        will only have a `.post()` handler.
    methods (list of str):
        A list of supported HTTP methods. The `all` built-in can be used
        to support all HTTP methods. Defaults to `["get"]`.

    # Returns
    view (View): a `View` instance.

    # See Also
    - The [constants](./constants.md) module for the list of all HTTP methods.
    """
    if methods is None:
        methods = ["get"]
    if methods is all:
        methods = ["handle"]
    else:
        methods = [m.lower() for m in methods]
    handlers = {method: handler for method in methods}
    return View.create(handler.__name__, handler.__doc__, handlers)


def from_obj(obj: Any) -> View:
    """Convert an object to a `View` instance.

    # Parameters
    obj (any):
        its handlers, snake-cased class name and docstring are copied
        onto the view.

    # Returns
    view (View): a `View` instance.
    """
    handlers = get_handlers(obj)
    name = camel_to_snake(obj.__class__.__name__)
    return View.create(name, obj.__doc__, handlers)


def get_handlers(obj: Any) -> Dict[str, Handler]:
    """Return all `View` handlers declared on an object.

    # Parameters
    obj (any): an object.

    # Returns
    handlers (dict):
        A dict mapping an HTTP method to a handler.
    """
    all_methods = map(str.lower, ALL_HTTP_METHODS)
    try:
        handle = obj.handle
    except AttributeError:
        return {
            method: getattr(obj, method)
            for method in all_methods
            if hasattr(obj, method)
        }
    else:
        return {method: handle for method in all_methods}


def view(methods: MethodsParam = None):
    """Convert the decorated function to a proper `View` object.

    This decorator is a shortcut for [from_handler](#from-handler).
    """
    return partial(from_handler, methods=methods)
