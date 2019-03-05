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
            if not await req.is_disconnected():
                yield item
                continue

            try:
                await source.athrow(ClientDisconnect)
            except StopAsyncIteration:
                # May be raised in Python 3.6 if the `source`'s error
                # handling code did not `yield` anything.
                break
            else:
                # Paranoia. We really need to break out of this loop.
                break

    return stream()
