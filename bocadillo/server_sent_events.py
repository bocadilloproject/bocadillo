import inspect
from json import dumps
from typing import Union, Optional, Awaitable, Callable, AsyncIterable

from starlette.requests import ClientDisconnect


class ServerSentEvent:
    __slots__ = ("data", "id", "name")

    def __init__(
        self,
        data: Optional[str] = None,
        id: Optional[int] = None,
        name: Optional[str] = None,
        json: Optional[Union[list, dict]] = None,
    ):
        self.data = data if json is None else dumps(json)
        self.id = id
        self.name = name

    def __str__(self):
        parts = []

        def _add_part(name: str, value: Optional[str]):
            if value is not None:
                parts.append(f"{name}: {value}")

        _add_part("id", self.id)
        _add_part("event", self.name)
        _add_part("data", self.data)
        parts.append("\n")

        return "\n".join(parts)


def server_event(*args, **kwargs) -> ServerSentEvent:
    return ServerSentEvent(*args, **kwargs)


def add_sse_headers(headers: dict) -> dict:
    return {
        # v Overridden by `headers`
        "cache-control": "no-cache",
        # ^
        **headers,
        # v Override `headers`
        "content-type": "text/event-stream",
        "connection": "keep-alive",
        # ^
    }


# TODO: add cleanup
class EventStream:
    def __init__(self, source: Callable[[], AsyncIterable]):
        assert inspect.isasyncgenfunction(source)
        self.source = source()

    async def __aiter__(self):
        async for event in self.source:
            yield str(event)
