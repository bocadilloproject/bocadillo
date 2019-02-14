import json
from typing import Any, Callable, TypeVar, Union, Dict

from .constants import CONTENT_TYPE

_V = TypeVar("_V")


MediaHandler = Callable[[Any], str]
Handlers = Dict[str, MediaHandler]


def handle_json(value: Union[dict, list]) -> str:
    """A media handler that dumps a value using `json.dumps`."""
    return json.dumps(value)


def get_default_handlers() -> Handlers:
    """Return the default media handlers.

    - `application/json`: [handle_json](#handle-json)
    """
    return {CONTENT_TYPE.JSON: handle_json}


class UnsupportedMediaType(Exception):
    """Raised when trying to use an unsupported media type.

    # Attributes
    media_type (str): the unsupported media type.
    handlers (dict): the dict of supported media handlers.
    """

    def __init__(self, media_type: str, handlers: Handlers):
        self.media_type = media_type
        self.handlers = handlers
        self._available = ", ".join(handlers.keys())

    def __str__(self):
        return f"{self.media_type} (available: {self._available})"
