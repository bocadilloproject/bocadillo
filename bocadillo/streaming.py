from typing import AnyStr, Callable, AsyncIterable
import inspect

Stream = AsyncIterable[AnyStr]
StreamFunc = Callable[[], Stream]


def stream_until_disconnect(req, source: Stream) -> Stream:
    # Yield items from a stream until the client disconnects.
    assert inspect.isasyncgen(source)

    async def stream():
        async for item in source:
            if await req.is_disconnected():
                break
            yield item

    return stream()
