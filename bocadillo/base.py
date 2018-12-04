"""Application base classes, interfaces and meta classes."""


class Applicable:
    """Base interface for "applicable" classes.

    This is a key interface for the recipes system.
    """

    def apply(self, other: 'Applicable', prefix: str):
        pass
