from typing import List

from .router import Router


class RoutingMixin:
    """Provide routing capabilities to a class."""

    def __init__(self):
        super().__init__()
        self._router = Router()

    def route(
        self,
        pattern: str,
        *,
        methods: List[str] = None,
        name: str = None,
        namespace: str = None,
    ):
        """Register a new route by decorating a view.

        # Parameters
        pattern (str):
            An URL pattern given as a format string.
        methods (list of str):
            HTTP methods supported by this route.
            Defaults to all HTTP methods.
            Ignored for class-based views.
        name (str):
            A name for this route, which must be unique. Defaults to
            a name based on the view.
        namespace (str):
            A namespace for this route (optional).
            If given, will be prefixed to the `name` and separated by a colon,
            e.g. `"blog:index"`.

        # Raises
        RouteDeclarationError:
            If any method is not a valid HTTP method,
            if `pattern` defines a parameter that the view does not accept,
            if the view uses a parameter not defined in `pattern`,
            if the `pattern` does not start with `/`,
            or if the view did not accept the `req` and `res` parameters.

        # Example
        ```python
        >>> import bocadillo
        >>> api = bocadillo.API()
        >>> @api.route("/greet/{person}")
        ... def greet(req, res, person: str):
        ...     pass
        ```
        """
        return self._router.route_decorator(
            pattern=pattern, methods=methods, name=name, namespace=namespace
        )

    def url_for(self, name: str, **kwargs) -> str:
        """Build the URL path for a named route.

        # Parameters
        name (str): the name of the route.
        kwargs (dict): route parameters.

        # Returns
        url (str): the URL path for a route.

        # Raises
        HTTPError(404) : if no route exists for the given `name`.
        """
        route = self._router.get_route_or_404(name)
        return route.url(**kwargs)
