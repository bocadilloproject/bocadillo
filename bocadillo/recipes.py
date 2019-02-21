from typing import Sequence

from .applications import App


class RecipeBase:
    """Definition of the recipe interface."""

    def __init__(self, prefix: str):
        assert prefix.startswith("/"), "recipe prefix must start with '/'"
        self.prefix = prefix

    def apply(self, app: App, root: str = ""):
        """Apply the recipe to an application.

        Should be implemented by subclasses.

        # Parameters
        app (App): an application instance.
        root (str): a root URL path.
        """
        raise NotImplementedError


class Recipe(App):
    """A grouping of capabilities that can be merged back into an application.

    # Parameters

    name (str):
        A name for the recipe.
    prefix (str):
        The path prefix where the recipe will be mounted.
        Defaults to `"/" + name`.
    """

    def __init__(self, name: str = None, prefix: str = None, **kwargs):
        super().__init__(name=name, **kwargs)

        if prefix is None:
            prefix = f"/{name}"
        assert prefix.startswith("/"), "recipe prefix must start with '/'"

        self.prefix = prefix
        # DEPRECATED: 0.13.0
        self._templates_dir_given = "templates_dir" in kwargs

    def _get_own_url_for(self, name: str, **kwargs) -> str:
        return self.prefix + super()._get_own_url_for(name, **kwargs)

    def apply(self, app: App, root: str = ""):
        """Apply the recipe to an application."""
        app.mount(prefix=root + self.prefix, app=self)

        # DEPRECATED: 0.13.0
        # Look for templates where the app does, if not specified
        if not self._templates_dir_given:
            self.templates_dir = app.templates_dir  # type: ignore

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

    def apply(self, app: App, root: str = ""):
        """Apply the recipe book to an application."""
        for recipe in self.recipes:
            recipe.apply(app, root=root + self.prefix)
