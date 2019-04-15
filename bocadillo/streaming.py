import typing
import inspect

from .request import Request, ClientDisconnect

Stream = typing.AsyncIterable[typing.AnyStr]
StreamFunc = typing.Callable[[], Stream]


def stream_until_disconnect(
    req: Request, source: Stream, raise_on_disconnect: bool
) -> Stream:
    # Yield items from a stream until the client disconnects, then
    # throw an exception into the stream (if told to do so).

    assert inspect.isasyncgen(source)

    async def stream():
        async for item in source:
            if not await req.is_disconnected():
                yield item
                continue

            if raise_on_disconnect:
                try:
                    await source.athrow(ClientDisconnect)
                except StopAsyncIteration:
                    # May be raised in Python 3.6 if the `source`'s error
                    # handling code did not `yield` anything.
                    break
            else:
                break

    return stream()
