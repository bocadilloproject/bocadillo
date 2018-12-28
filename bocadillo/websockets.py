from typing import Awaitable, Callable

from starlette.websockets import WebSocket as StarletteWebSocket


class WebSocket(StarletteWebSocket):
    async def __aenter__(self, *args, **kwargs):
        await self.accept()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()


WebSocketView = Callable[[WebSocket], Awaitable[None]]
