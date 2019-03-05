from json import dumps
from typing import Any, Optional


def _format_server_sent_event(**parts: Optional[Any]) -> str:
    return (
        "\n".join(
            f"{name}: {value}"
            for name, value in parts.items()
            if value is not None
        )
        + "\n\n"
    )


class server_event(str):
    """A string-like object that represents a Server-Sent Event.

    # Parameters
    data (str):
        The event data line(s), as defined in the SSE standard.
    id (int):
        The event ID, as defined in the SSE standard.
    name (str):
        The event name, as defined in the SSE standard.
    json (list or dict):
        A JSON-serializable value. If given, it is serialized and used as
        `data`.
    """

    __slots__ = ("data", "id", "name")

    def __new__(
        cls,
        data: Optional[str] = None,
        id: Optional[int] = None,
        name: Optional[str] = None,
        json: Optional[Any] = None,
    ):
        if json is not None:
            data = dumps(json)

        message = _format_server_sent_event(id=id, event=name, data=data)

        self = super().__new__(cls, message)

        self.data = data
        self.name = name
        self.id = id

        return self
