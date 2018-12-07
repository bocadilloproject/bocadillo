from typing import List

from .hooks import HooksMixin, Hooks, HookFunction
from .templates import TemplatesMixin


class RecipeRoute:
    """A mock route to be stored in a recipe.

    The route can be registered later on an API object.
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
        # Build the route.
        route = api.route(prefix + self._pattern, *self._args, **self._kwargs)(
            self._view
        )

        # Register hooks registered via @before and/or @after on top of
        # the @route decorator.
        def _register_hook(hook, register):
            nonlocal self, route
            if self.hooks.get(hook) is None:
                return
            hook_function = self.hooks[hook]
            route = register(hook_function)(route)

        _register_hook('before', api.before)
        _register_hook('after', api.after)


class RecipeHooks(Hooks[RecipeRoute]):
    """A custom hooks manager for recipes."""

    route_class = RecipeRoute

    def store_hook(
        self, hook: str, hook_function: HookFunction, route: RecipeRoute
    ):
        # Store the hook on the RecipeRoute object
        route.hooks[hook] = hook_function


class Recipe(TemplatesMixin, HooksMixin):
    """A grouping of capabilities that can be merged back into an API.

    # Parameters

    name (str):
        A name for the recipe.
    prefix (str):
        The path prefix where the recipe will be mounted.
        Defaults to `'/' + name`.
    templates_dir (str):
        See #API.
    """

    hooks_manager_class = RecipeHooks

    def __init__(self, name: str, prefix: str = None, **kwargs):
        super().__init__(**kwargs)
        if prefix is None:
            prefix = f'/{name}'
        assert prefix.startswith('/'), 'recipe prefix must start with "/"'
        self._name = name
        self._prefix = prefix
        self._routes: List[RecipeRoute] = []

    def route(self, *args, **kwargs):
        def register(view):
            route = RecipeRoute(*args, view=view, **kwargs)
            self._routes.append(route)
            return route

        return register

    def apply(self, api):
        # Apply routes on the API
        for route in self._routes:
            route.register(api, self._prefix)

        # Look for templates where the API does, if not specified
        if self.templates_dir is None:
            self.templates_dir = api.templates_dir
