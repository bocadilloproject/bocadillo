"""Application meta classes."""
from collections import OrderedDict

from .hooks import HooksMixin
from .routing import RoutingMixin


class APIMeta(type):
    """Metaclass for API."""

    _bases_with_docs = [HooksMixin, RoutingMixin]

    def __new__(mcs, name, bases, namespace):
        mcs._prepare_for_docs(bases, namespace)
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

    @classmethod
    def _prepare_for_docs(mcs, bases, namespace):
        # Pydoc-Markdown only takes documented members from the class'
        # `__dict__`. This is not added automatically when subclassing, so
        # we need to force it.
        for base in filter(mcs._should_include_docs, bases):
            for key, value in base.__dict__.items():
                if key in namespace:
                    # Don't prevent overriding on API class
                    continue
                namespace[key] = value

    @classmethod
    def _should_include_docs(mcs, base):
        return any(issubclass(base, other) for other in mcs._bases_with_docs)
