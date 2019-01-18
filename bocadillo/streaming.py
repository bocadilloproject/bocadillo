from typing import AnyStr, Callable, AsyncIterable
import inspect

from .request import Request, ClientDisconnect

Stream = AsyncIterable[AnyStr]
StreamFunc = Callable[[], Stream]


def stream_until_disconnect(req: Request, source: Stream) -> Stream:
    # Yield items from a stream until the client disconnects, then
    # throw an exception into the stream.
    assert inspect.isasyncgen(source)

    async def stream():
        async for item in source:
            if await req.is_disconnected():
                await source.athrow(ClientDisconnect)
            yield item

    return stream()
