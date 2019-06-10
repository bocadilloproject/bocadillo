import inspect
import typing

from . import injection
from .app_types import Handler
from .compat import check_async
from .constants import ALL_HTTP_METHODS
from .converters import ViewConverter, convert_arguments
from .errors import HTTPError

MethodsParam = typing.Union[typing.List[str], all]  # type: ignore


class HandlerDoesNotExist(Exception):
    # Raised to signal that no handler exists for a requested HTTP method.
    pass


class HTTPConverter(ViewConverter):
    def get_query_params(self, args, kwargs):
        req = args[0]
        return req.query_params


def get_handlers(obj: typing.Any) -> typing.Dict[str, typing.Callable]:
    if hasattr(obj, "handle"):
        return {method: obj.handle for method in ALL_HTTP_METHODS}
    return {
        method: getattr(obj, method)
        for method in ALL_HTTP_METHODS
        if hasattr(obj, method)
    }


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
    """

    __slots__ = (
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "handle",
    )

    get: Handler
    post: Handler
    put: Handler
    patch: Handler
    delete: Handler
    head: Handler
    options: Handler
    handle: Handler

    def __init__(self, obj: typing.Any, methods: typing.List[str] = None):
        if isinstance(obj, View):
            raise NotImplementedError
        if inspect.isclass(obj):
            # View-like class.
            name = obj.__name__
            class_based = True
            handlers = get_handlers(obj())
        elif callable(obj):
            # Function-based view.
            name = obj.__name__
            class_based = False
            if methods is None:
                methods = ["get"]
            if methods is all:
                methods = ["handle"]
            else:
                methods = [m.lower() for m in methods]
            handlers = {method: obj for method in methods}
        else:
            # Treat as a view-like object.
            name = obj.__class__.__name__
            class_based = True
            handlers = get_handlers(obj)

        for method, handler in handlers.items():
            full_name = f"{name}.{method.lower()}" if class_based else name
            check_async(
                handler, reason=(f"view '{full_name}()' must be asynchronous")
            )

        copy_get_to_head = "get" in handlers and "head" not in handlers
        if copy_get_to_head:
            handlers["head"] = handlers["get"]

        for method, handler in handlers.items():
            handler = convert_arguments(handler, converter_class=HTTPConverter)
            handler = injection.consumer(handler)
            setattr(self, method, handler)

    async def __call__(self, req, res, **params):
        try:
            handler = getattr(self, "handle")
        except AttributeError:
            try:
                handler = getattr(self, req.method.lower())
            except AttributeError:
                raise HTTPError(405)
        await handler(req, res, **params)
