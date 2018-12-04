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

    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self._prefix = f'/{name}'

    @property
    def prefix(self):
        return self._prefix
