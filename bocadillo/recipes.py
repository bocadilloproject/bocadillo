from .base import Applicable
from .hooks import HooksMixin
from .routing import RoutingMixin
from .templates import TemplatesMixin


class Recipe(HooksMixin, TemplatesMixin, RoutingMixin, Applicable):
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

    @property
    def prefix(self):
        return self._prefix

    def route(self, pattern: str, *args, **kwargs):
        return super().route(pattern, *args, **kwargs)
