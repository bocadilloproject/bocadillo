import json
from typing import Any, Optional, Callable, Dict

from .exceptions import UnsupportedMediaType

MediaHandler = Callable[[Any], str]


def handle_json(value: dict) -> str:
    return json.dumps(value)


def handle_text(value: Any) -> str:
    return str(value)


def get_default_handlers() -> dict:
    return {
        Media.JSON: handle_json,
        Media.PLAIN_TEXT: handle_text,
        Media.HTML: handle_text,
    }


class Media:
    """Registry of media handlers."""

    JSON = "application/json"
    PLAIN_TEXT = "text/plain"
    HTML = "text/html"

    def __init__(
        self, media_type: str, handlers: Dict[str, MediaHandler] = None
    ):
        """Create a media registry.

        Parameters
        -----------
        media_type : str
            The default media type that will be used when serializing values.
        handlers : dict of str -> MediaHandler, optional
            A mapping of media type to an (Any) -> str callable.
            Defaults to built-in media handlers.
        """
        if handlers is None:
            handlers = get_default_handlers()
        self.handlers = handlers
        self.type = media_type

    def serialize(self, value: Any, media_type: Optional[str] = None):
        """Serialize a value using the given media type.

        Parameters
        ----------
        value : any
        media_type : str, optional
            The media type of the given value. Determines which media handler
            is used.
            Defaults to the media registry's media type.
        """
        if media_type is None:
            media_type = self.type
        handler = self.handlers[media_type]
        return handler(value)

    @property
    def type(self) -> str:
        """Return the default media type."""
        return self._default_type

    @type.setter
    def type(self, media_type: str):
        """Set the default media type.

        Parameters
        ----------
        media_type : str

        Raises
        ------
        UnsupportedMediaType :
            If no handler exists for the given media type.
        """
        if media_type not in self.handlers:
            raise UnsupportedMediaType(
                media_type, available=list(self.handlers)
            )
        self._default_type = media_type
