"""Routing check and validation utilities."""
import inspect
from string import Formatter
from typing import List

from .exceptions import RouteDeclarationError
from ..constants import ALL_HTTP_METHODS
from ..view import get_declared_method_views, View, get_view_name


def check_route(pattern: str, view: View, methods: List[str]) -> None:
    """Check compatibility of a route pattern and a view."""
    view_name = get_view_name(view)
    _check_methods(methods, view_name)
    _check_route_pattern(pattern, view_name)
    _check_route_parameters(pattern, view)


def _check_methods(methods: List[str], view_name: str) -> None:
    for method in methods:
        if method not in ALL_HTTP_METHODS:
            raise RouteDeclarationError(
                f"Route '{view_name}' accepts method '{method}' "
                "but it is not one of the valid HTTP methods: "
                f"{', '.join(ALL_HTTP_METHODS)}"
            )


def _check_route_pattern(pattern: str, view_name: str) -> None:
    if not pattern.startswith("/"):
        raise RouteDeclarationError(
            f"Route pattern '{pattern}' on view '{view_name}' "
            f"must start with '/' to avoid ambiguities."
        )


def _check_route_parameters(pattern: str, view: View, _base=None) -> None:
    """Verify that a view accepts parameters defined in a route pattern.

    Raises
    ------
    RouteDeclarationError :
        If a route parameter is not one of the view's arguments,
        of a view argument was not declared in the route pattern.
    """

    parsed_format = Formatter().parse(pattern)
    route_parameters: set = {name for _, name, _, _ in parsed_format if name}

    if callable(view):
        view_name = get_view_name(view=view, base=_base)
        view_parameters = dict(inspect.signature(view).parameters)

        # Necessary if view is from a class-based view.
        view_parameters.pop("self", None)

        for route_param in route_parameters:
            if route_param not in view_parameters:
                raise RouteDeclarationError(
                    f"Parameter '{route_param}' was declared on route "
                    f"'{view_name}()' and should be one of "
                    "its arguments."
                )

        if len(view_parameters) < 2:
            raise RouteDeclarationError(
                f"View '{view_name}' must have at least two "
                "parameters (request and response)."
            )

        for i, view_param in enumerate(view_parameters):
            is_req_or_res = i < 2
            if is_req_or_res:
                continue
            if view_param not in route_parameters:
                raise RouteDeclarationError(
                    f"Parameter '{view_param}' is expected by route "
                    f"'{view_name}' but was not declared in the "
                    "route pattern."
                )
    else:
        for method, method_view in get_declared_method_views(view):
            _check_route_parameters(pattern, method_view, _base=view)
