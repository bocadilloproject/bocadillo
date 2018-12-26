from typing import List, Sequence

from bocadillo.meta import DocsMeta
from .hooks import HooksMixin, HooksBase, HookFunction
from .templates import TemplatesMixin


class RecipeRoute:
    """A specific kind of route for recipes.

    The route will be registered an actual API object during `recipe.apply()`.

    Mostly an implementation detail.
    """

    def __init__(self, pattern, view, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._pattern = pattern
        self._view = view
        self.hooks = {}

    def register(self, api, prefix: str) -> None:
        """Register the route on the API object at the given prefix.

        # Parameters

        api (API):
            A Bocadillo application.
        prefix (str):
            A path prefix.
        """
        route = api.route(prefix + self._pattern, *self._args, **self._kwargs)(
            self._view
        )

        # Hooks registered via @before and/or @after on top of the @route
        # decorator need to be manually registered with @api.before, @api.after.
        def _register_hook(hook, hook_decorator):
            nonlocal self, route
            if self.hooks.get(hook) is None:
                return
            hook_function = self.hooks[hook]
            route = hook_decorator(hook_function)(route)

        _register_hook("before", api.before)
        _register_hook("after", api.after)


class RecipeHooks(HooksBase):
    """A specific hooks manager for recipes.

    Mostly an implementation detail.
    """

    __route_class__ = RecipeRoute

    def store_hook(
        self, hook: str, hook_function: HookFunction, route: RecipeRoute
    ):
        route.hooks[hook] = hook_function


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


class Recipe(TemplatesMixin, HooksMixin, RecipeBase, metaclass=DocsMeta):
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

    __hooks_manager_class__ = RecipeHooks

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
