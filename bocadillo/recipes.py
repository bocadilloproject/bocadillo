from typing import List

from .hooks import with_hook, ensure_async_hook_function
from .templates import TemplatesMixin


class RecipeRoute:
    def __init__(self, pattern, view, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._pattern = pattern
        self._view = view
        self.hooks = {}

    def register(self, api, prefix: str):
        route = api.route(prefix + self._pattern, *self._args, **self._kwargs)(
            self._view
        )

        def _register_hook(hook, register):
            nonlocal self, route
            if self.hooks.get(hook) is None:
                return
            hook_function, args, kwargs = self.hooks[hook]
            route = register(hook_function, *args, **kwargs)(route)

        _register_hook('before', api.before)
        _register_hook('after', api.after)


class Recipe(TemplatesMixin):
    """A grouping of capabilities that can be merged back into an API.

    # Supported capabilities

    - Templates
    - Hooks
    - Routing
    """

    def __init__(self, name: str, prefix: str = None, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        if prefix is None:
            prefix = f'/{name}'
        assert prefix.startswith('/'), 'recipe prefix must start with "/"'
        self._prefix = prefix
        self._routes: List[RecipeRoute] = []

    @property
    def prefix(self):
        return self._prefix

    def route(self, pattern: str, *args, **kwargs):
        def register(view):
            route = RecipeRoute(pattern=pattern, view=view, *args, **kwargs)
            self._routes.append(route)
            return route

        return register

    def before(self, hook_function, *args, **kwargs):
        return self._hook('before', hook_function, *args, **kwargs)

    def after(self, hook_function, *args, **kwargs):
        return self._hook('after', hook_function, *args, **kwargs)

    def _hook(self, hook, hook_function, *args, **kwargs):
        def register(hookable):
            nonlocal hook_function
            if isinstance(hookable, RecipeRoute):
                hookable.hooks[hook] = (hook_function, args, kwargs)
                return hookable
            else:
                hook_function = ensure_async_hook_function(
                    hook_function, *args, **kwargs
                )
                return with_hook(hookable, hook, hook_function)

        return register

    def apply(self, api):
        for route in self._routes:
            route.register(api, self._prefix)

        if self.templates_dir is None:
            self.templates_dir = api.templates_dir
