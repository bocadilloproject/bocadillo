import inspect
from string import Formatter
from typing import Callable, Union, Type, Any

from bocadillo.routing import BaseRoute, BaseRouter
from . import views
from .app_types import HTTPApp
from .errors import HTTPError
from .redirection import Redirection
from .request import Request
from .response import Response
from .views import View, HandlerDoesNotExist
from ..meta import DocsMeta


# Routes


class HTTPRoute(BaseRoute, metaclass=DocsMeta):
    """Represents the binding of an URL pattern to an HTTP view.

    # Parameters
    pattern (str): an URL pattern. F-string syntax is supported for parameters.
    view (View):
        A `View` object.
    name (str):
        The route's name.
    """

    def __init__(self, pattern: str, view: View, name: str):
        super().__init__(pattern)
        self._view = view
        self._name = name

    async def __call__(self, req: Request, res: Response, **params) -> None:
        try:
            await self._view(req, res, **params)
        except HandlerDoesNotExist as e:
            raise HTTPError(405) from e


class HTTPRouter(HTTPApp, BaseRouter[HTTPRoute]):
    # A collection of HTTP routes.

    def add_route(
        self,
        view: Union[View, Type[Any], Callable, Any],
        pattern: str,
        *,
        name: str = None,
        namespace: str = None,
    ) -> HTTPRoute:
        # Build and register a route.

        if isinstance(view, View):
            # View instance. No further conversion required.
            pass
        elif inspect.isclass(view):
            # View-like class.
            view = views.from_obj(view())
        elif callable(view):
            # Function-based view.
            # NOTE: here, we ensure backward-compatibility with the routing of
            # function-based views pre-0.9.
            view = views.from_handler(view)
        else:
            # View-like object.
            view = views.from_obj(view)

        assert isinstance(view, View)

        if name is None:
            name = view.name
        if namespace is not None:
            name = namespace + ":" + name

        check_route(pattern, view)

        route = HTTPRoute(pattern=pattern, view=view, name=name)
        self.routes[name] = route

        return route

    def get_route_or_404(self, name: str) -> HTTPRoute:
        # Return a route or raise a 404 error.
        try:
            return self.routes[name]
        except KeyError as e:
            raise HTTPError(404) from e

    async def __call__(self, req: Request, res: Response) -> Response:
        match = self.match(req.url.path)
        if match is None:
            raise HTTPError(status=404)
        try:
            await match.route(req, res, **match.params)
        except Redirection as redirection:
            res = redirection.response
        return res


def check_route(pattern: str, view: View) -> None:
    """Check compatibility of a route pattern and a view.

    # Parameters
    pattern (str): an URL pattern.
    view (View): a `View` object.

    # Raises
    RouteDeclarationError :
        - If `pattern` does not have a leading slash.
        - If route parameters declared in the pattern do not match those
        of any view handler, e.g. a parameter is declared in the pattern, but
        not used in the handler or vice-versa.

    # See Also
    - `ALL_HTTP_METHODS` is defined in [constants.py](./constants.md).
    """
    if not pattern.startswith("/"):
        raise RouteDeclarationError(
            f"Route pattern '{pattern}' on view '{view.name}' "
            f"must start with '/' to avoid ambiguities."
        )

    parsed_format = Formatter().parse(pattern)
    route_parameters: set = {name for _, name, _, _ in parsed_format if name}

    for method, handler in views.get_handlers(view).items():
        handler_parameters = dict(inspect.signature(handler).parameters)
        handler_parameters.pop("self", None)  # paranoia check
        handler_parameters = list(handler_parameters)

        for route_param in route_parameters:
            if route_param not in handler_parameters:
                raise RouteDeclarationError(
                    f"Route pattern '{pattern}' declares the route parameter "
                    f"'{route_param}' and should be a parameter of "
                    f"'{handler.__qualname__}'."
                )

        for handler_param in handler_parameters[2:]:
            if handler_param not in route_parameters:
                raise RouteDeclarationError(
                    f"Handler '{handler.__qualname__}' expects parameter "
                    f"'{handler_param}' but it was not declared in the route "
                    f"pattern '{pattern}'"
                )


class RouteDeclarationError(Exception):
    """Raised when a route is ill-declared."""
