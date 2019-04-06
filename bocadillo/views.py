import inspect
from functools import partial, wraps
from typing import Any, cast, Dict, List, Optional, Type, Union

from . import injection
from .app_types import AsyncHandler, Handler
from .compat import call_async, camel_to_snake
from .constants import ALL_HTTP_METHODS
from .converters import ViewConverter, convert_arguments

MethodsParam = Union[List[str], all]  # type: ignore


class HandlerDoesNotExist(Exception):
    # Raised to signal that no handler exists for a requested HTTP method.
    pass


class HTTPConverter(ViewConverter):
    def get_query_params(self, args, kwargs):
        req = args[0]
        return req.query_params


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

    __slots__ = (
        "name",
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "handle",
    )

    def __init__(self, name: str):
        self.name = name

    get: AsyncHandler
    post: AsyncHandler
    put: AsyncHandler
    patch: AsyncHandler
    delete: AsyncHandler
    head: AsyncHandler
    options: AsyncHandler
    handle: AsyncHandler

    @staticmethod
    def _to_all_async(handlers: Dict[str, Handler]) -> Dict[str, AsyncHandler]:
        async_handlers: Dict[str, AsyncHandler] = {}

        for method, handler in handlers.items():
            if not inspect.iscoroutinefunction(handler):
                handler = wraps(handler)(partial(call_async, handler))
            async_handlers[method] = cast(AsyncHandler, handler)

        return async_handlers

    @classmethod
    def create(
        cls: Type["View"], name: str, handlers: Dict[str, Handler]
    ) -> "View":
        async_handlers: Dict[str, AsyncHandler] = cls._to_all_async(handlers)

        copy_get_to_head = (
            "get" in async_handlers and "head" not in async_handlers
        )
        if copy_get_to_head:
            async_handlers["head"] = async_handlers["get"]

        vue: View = cls(name)

        for method, handler in async_handlers.items():
            handler = convert_arguments(handler, converter_class=HTTPConverter)
            handler = injection.consumer(handler)
            setattr(vue, method, handler)

        return vue

    def get_handler(self, method: str) -> AsyncHandler:
        try:
            return getattr(self, "handle")
        except AttributeError:
            try:
                return getattr(self, method)
            except AttributeError as exc:
                raise HandlerDoesNotExist from exc


def from_handler(handler: Handler, methods: MethodsParam = None) -> View:
    """Convert a handler to a #::bocadillo.views#View instance.

    # Parameters
    handler (function or coroutine function):
        Its name is copied onto the view.
        It used as a handler for each of the declared `methods`.
        For example, if `methods=["post"]` then the returned `view` object
        will only have a `.post()` handler.
    methods (list of str):
        A list of supported HTTP methods. The `all` built-in can be used
        to support all HTTP methods. Defaults to `["get"]`.

    # Returns
    view: a #::bocadillo.views#View instance.

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
    return View.create(handler.__name__, handlers)


def from_obj(obj: Any) -> View:
    """Convert an object to a #::bocadillo.views#View instance.

    # Parameters
    obj (any):
        its handlers and snake-cased class name are copied onto the view.

    # Returns
    view: a #::bocadillo.views#View instance.
    """
    handlers = get_handlers(obj)
    name = camel_to_snake(obj.__class__.__name__)
    return View.create(name, handlers)


def get_handlers(obj: Any) -> Dict[str, Handler]:
    """Return all #::bocadillo.views#View handlers declared on an object.

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
    """Convert the decorated function to a proper #::bocadillo.views#View.

    This decorator is a shortcut for [from_handler](#from-handler).
    """
    return partial(from_handler, methods=methods)
