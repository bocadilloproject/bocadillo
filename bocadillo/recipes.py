import typing

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
        app: an #::bocadillo.applications#App instance.
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

    def __init__(self, name: str, prefix: str = None, **kwargs):
        super().__init__(name=name, **kwargs)

        if prefix is None:
            prefix = f"/{name}"
        assert prefix.startswith("/"), "recipe prefix must start with '/'"

        self.prefix = prefix

    def apply(self, app: App, root: str = ""):
        """Apply the recipe to an application."""
        app.mount(prefix=root + self.prefix, app=self)

    @classmethod
    def book(cls, *recipes: "Recipe", prefix: str) -> "RecipeBook":
        """Build a book of recipes.

        Shortcut for `RecipeBook(recipes, prefix)`.
        """
        return RecipeBook(recipes, prefix)


class RecipeBook(RecipeBase):
    """A composition of multiple recipes.

    # Parameters
    recipes (list): a list of #::bocadillo.recipes#Recipe objects.
    prefix (str):
        A prefix that will be prepended to all of the recipes' prefixes.
    """

    def __init__(self, recipes: typing.Sequence[Recipe], prefix: str):
        super().__init__(prefix)
        self.recipes = recipes

    def apply(self, app: App, root: str = ""):
        """Apply the recipe book to an application."""
        for recipe in self.recipes:
            recipe.apply(app, root=root + self.prefix)
