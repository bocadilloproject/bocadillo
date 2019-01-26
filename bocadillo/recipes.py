from typing import Sequence, Tuple, Any

from .meta import DocsMeta
from .templates import TemplatesMixin
from .routing import BaseRouter


RecipeRoute = Tuple[Any, str, dict]


class RecipeRouter(BaseRouter[RecipeRoute]):
    def __init__(self):
        super().__init__()
        self.routes = []

    def add_route(self, view: Any, pattern: str, **kwargs: Any) -> RecipeRoute:
        route = (view, pattern, kwargs)
        self.routes.append(route)
        return route


class RecipeBase:
    """Definition of the recipe interface."""

    def __init__(self, prefix: str):
        assert prefix.startswith("/"), "recipe prefix must start with '/'"
        self.prefix = prefix

    def __call__(self, api, root: str = ""):
        """Apply the recipe to an API object.

        Should be implemented by subclasses.

        # Parameters
        api (API): an API object.
        root (str): a root URL path.
        """
        raise NotImplementedError


class Recipe(TemplatesMixin, RecipeBase, metaclass=DocsMeta):
    """A grouping of capabilities that can be merged back into an API.

    # Parameters

    name (str):
        A name for the recipe.
    prefix (str):
        The path prefix where the recipe will be mounted.
        Defaults to `"/" + name`.
    templates_dir (str):
        See #API.
    """

    def __init__(self, name: str, prefix: str = None, **kwargs):
        if prefix is None:
            prefix = f"/{name}"
        super().__init__(prefix=prefix, **kwargs)
        self.name = name
        self.http_router = RecipeRouter()
        self.websocket_router = RecipeRouter()

    def route(self, pattern: str, **kwargs):
        """Register a route on the recipe.

        Accepts the same arguments as `API.route()`, except `namespace` which
        will be given the value of the recipe's `name`.

        # See Also
        - [API.route()](./api.md#route)
        """
        kwargs["namespace"] = self.name
        return self.http_router.route(pattern=pattern, **kwargs)

    def websocket_route(self, pattern: str, **kwargs):
        """Register a WebSocket route on the recipe.

        Accepts the same arguments as `API.websocket_route()`.

        # See Also
        - [API.websocket_route()](./api.md#websocket-route)
        """
        return self.websocket_router.route(pattern=pattern, **kwargs)

    def __call__(self, api, root: str = ""):
        """Apply the recipe to an API object."""
        # Apply routes on the API
        for view, pattern, kwargs in self.http_router.routes:
            api.route(root + self.prefix + pattern, **kwargs)(view)
        for view, pattern, kwargs in self.websocket_router.routes:
            api.websocket_route(root + self.prefix + pattern, **kwargs)(view)

        # Look for templates where the API does, if not specified
        if self.templates_dir is None:
            self.templates_dir = api.templates_dir

    @classmethod
    def book(cls, *recipes: "Recipe", prefix: str) -> "RecipeBook":
        """Build a book of recipes.

        Shortcut for `RecipeBook(recipes, prefix)`.
        """
        return RecipeBook(recipes, prefix)


class RecipeBook(RecipeBase):
    """A composition of multiple recipes.

    # Parameters
    recipes (list): a list of `Recipe` objects.
    prefix (str):
        A prefix that will be prepended to all of the recipes' prefixes.
    """

    def __init__(self, recipes: Sequence[Recipe], prefix: str):
        super().__init__(prefix)
        self.recipes = recipes

    def __call__(self, api, root: str = ""):
        """Apply the recipe book to an API object."""
        for recipe in self.recipes:
            recipe(api, root=root + self.prefix)
