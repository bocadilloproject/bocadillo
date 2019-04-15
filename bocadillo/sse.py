from json import dumps
import typing


class server_event(str):
    """A string-like object that represents a [Server-Sent Event][sse].

    [sse]: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format

    # Examples

    ```python
    >>> from bocadillo import server_event
    # Empty event
    >>> server_event()
    '\\n\\n'
    # Event with data
    >>> server_event("hello, world")
    'data: hello, world\\n\\n'
    # Named event with JSON data
    >>> server_event(name="userconnect", json={"username": "bobby"})
    'event: userconnect\\ndata: {"username": "bobby"}\\n\\n'
    ```

    # Parameters
    name (str):
        An optional `name` for the event.
    data (str or sequence):
        The event `data`. A sequence of strings can be given for
        multi-line event data.
    json (any):
        A JSON-serializable value which, if given, is serialized and used as
        `data`.
    id (int):
        An optional `id` for the event.
    """

    def __new__(
        cls,
        name: str = None,
        *,
        data: typing.Union[str, typing.Sequence] = None,
        json: typing.Any = None,
        id: int = None,
    ):
        if json is not None:
            data = dumps(json)

        parts = [("id", id), ("event", name)]

        if isinstance(data, str):
            parts.append(("data", data))
        elif data is not None:
            for item in data:
                parts.append(("data", item))

        sse_message = (
            "\n".join(
                f"{field}: {value}"
                for field, value in parts
                if value is not None
            )
            + "\n\n"
        )

        return super().__new__(cls, sse_message)

    # For API reference docs and IDE discovery only.
    def __init__(
        self,
        name: str = None,
        *,
        data: typing.Union[str, typing.Sequence] = None,
        json: typing.Any = None,
        id: int = None,
    ):
        pass
