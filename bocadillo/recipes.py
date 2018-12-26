from typing import List, Sequence

from .meta import DocsMeta
from .templates import TemplatesMixin


class RecipeBase:
    """Definition of the recipe interface."""

    def apply(self, api, root: str = ""):
        """Apply the recipe to an API object.

        Should be implemented by subclasses.

        # Parameters
        api (API): an API object.
        root (str): a root URL path itself prefixed to the recipe's `prefix`.
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
        super().__init__(**kwargs)
        if prefix is None:
            prefix = f"/{name}"
        assert prefix.startswith("/"), "recipe prefix must start with '/'"
        self._name = name
        self._prefix = prefix
        self._routes: List[RecipeRoute] = []

    def route(self, *args, **kwargs):
        """Register a route on the recipe.

        Accepts the same arguments as `API.route()`, except `namespace` which
        is given the value of the recipe's `name`.

        # See Also
        - [API.route()](./api.md#route)
        """

        def register(view):
            route = RecipeRoute(
                *args, view=view, namespace=self._name, **kwargs
            )
            self._routes.append(route)
            return route

        return register

    def apply(self, api, root: str = ""):
        """Apply the recipe to an API object.

        This will:

        - Mount registered routes onto the `api`.
        - Update the templates directory to that of `api`.

        # See Also
        - [RecipeBase.apply()](#apply)
        """
        # Apply routes on the API
        for route in self._routes:
            route.register(api, root + self._prefix)

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
        A prefix that will be prepended to all of the recipes' own prefixes.
    """

    def __init__(self, recipes: Sequence[Recipe], prefix: str):
        self.recipes = recipes
        self.prefix = prefix

    def apply(self, api, root: str = ""):
        """Apply the recipe book to an API object.

        This is equivalent to calling `recipe.apply(api, root=root + self.prefix)`
        for each of the book's recipes.

        # See Also
        - [RecipeBase.apply()](#apply)
        """
        for recipe in self.recipes:
            recipe.apply(api, root=root + self.prefix)
