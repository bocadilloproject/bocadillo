"""Start-up check and validation utilities."""
import inspect
from string import Formatter

from .exceptions import RouteDeclarationError
from .view import get_declared_method_views, View


def check_route_parameters(pattern: str, view: View, _base=None) -> None:
    """Verify that a view accepts parameters defined in a route pattern.

    Raises
    ------
    RouteDeclarationError :
        If a route parameter is not one of the view's arguments,
        of a view argument was not declared in the route pattern.
    """

    def _get_view_name():
        return '.'.join(arg.__name__ for arg in (_base, view) if arg)

    parsed_format = Formatter().parse(pattern)
    route_parameters: set = {name for _, name, _, _ in parsed_format if name}

    if inspect.isclass(view):
        views = get_declared_method_views(view)
        for method_view in views:
            check_route_parameters(pattern, method_view, _base=view)
    else:
        view_name = _get_view_name()
        view_parameters = inspect.signature(view).parameters

        # necessary if view is from a class-based view
        # view_parameters.pop('self', None)

        for route_param in route_parameters:
            if route_param not in view_parameters:
                raise RouteDeclarationError(
                    f'Parameter "{route_param}" was declared on route '
                    f'"{view_name}()" and should be one of '
                    'its arguments.'
                )

        for i, view_param in enumerate(view_parameters):
            is_req_or_res = i < 2
            if is_req_or_res:
                continue
            if view_param not in route_parameters:
                raise RouteDeclarationError(
                    f'Parameter "{view_param}" is expected by route '
                    f'"{view_name}" but was not declared in the '
                    'route pattern.'
                )
