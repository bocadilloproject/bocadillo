from json import dumps
from typing import Any, Union, Sequence, Optional


def _format_server_sent_event(
    data: Union[str, Sequence] = None, **parts: Optional[Any]
) -> str:
    part_items = list(parts.items())

    if isinstance(data, str):
        part_items.append(("data", data))
    elif data is not None:
        for item in data:
            part_items.append(("data", item))

    return (
        "\n".join(
            f"{name}: {value}"
            for name, value in part_items
            if value is not None
        )
        + "\n\n"
    )


class server_event(str):
    """A string-like object that represents a [Server-Sent Event][sse].

    [sse]: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format

    # Examples

    ```python
    # Empty event
    >>> print(server_event())
    '\n\n'
    # Event with data
    >>> server_event("hello, world")
    'data: hello, world\n\n'
    # Named event with JSON data
    >>> server_event(name="userconnect", json={"username": "bobby"})
    'event: userconnect\ndata: {"username": "bob"}\n\n'
    >>>
    ```

    # Parameters
    data (str or sequence):
        The event `data`. A sequence of strings can be given for
        multi-line event data.
    name (str):
        An optional `name` for the event.
    id (int):
        An optional `id` for the event.
    json (any):
        A JSON-serializable value which, if given, is serialized and used as
        `data`.
    """

    __slots__ = ("data", "id", "name")

    def __new__(
        cls,
        data: Optional[Union[str, Sequence]] = None,
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
