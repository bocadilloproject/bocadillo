"""Meta classes."""


class APIMeta(type):
    """Metaclass for API."""

    def __new__(mcs, name, bases, namespace):
        mcs._prepare_for_docs(bases, namespace)
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

    @classmethod
    def _prepare_for_docs(mcs, bases, namespace):
        # Pydoc-Markdown only takes documented members from the class'
        # `__dict__`. This is not added automatically when subclassing, so
        # we need to force it.
        for base in bases:
            for key, value in base.__dict__.items():
                if key.startswith("_"):
                    # Don't include private attributes and methods
                    continue
                if key in namespace:
                    # Don't prevent overriding on API class
                    continue
                namespace[key] = value
