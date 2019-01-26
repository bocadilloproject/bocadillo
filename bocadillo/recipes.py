from typing import Sequence


from .meta import DocsMeta
from .misc import overrides
from .routing import HTTPRoute, RoutingMixin, WebSocketRoute
from .templates import TemplatesMixin


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


class Recipe(TemplatesMixin, RoutingMixin, RecipeBase, metaclass=DocsMeta):
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

    def get_template_globals(self):
        return {"url_for": self.url_for}

    @overrides(RoutingMixin.route)
    def route(self, pattern: str, **kwargs) -> HTTPRoute:
        kwargs["namespace"] = self.name
        return super().route(self.prefix + pattern, **kwargs)

    @overrides(RoutingMixin.websocket_route)
    def websocket_route(self, pattern: str, **kwargs) -> WebSocketRoute:
        return super().websocket_route(self.prefix + pattern, **kwargs)

    def __call__(self, obj, root: str = ""):
        """Apply the recipe to an object.
        
        Said object must be a subclass `RoutingMixin` and `TemplateMixin`.
        """
        obj.http_router.mount(self.http_router, root=root)
        obj.websocket_router.mount(self.websocket_router, root=root)

        # Look for templates where the API does, if not specified
        if self.templates_dir is None:
            self.templates_dir = obj.templates_dir

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

    def __call__(self, api: RoutingMixin, root: str = ""):
        """Apply the recipe book to an API object."""
        for recipe in self.recipes:
            recipe(api, root=root + self.prefix)
