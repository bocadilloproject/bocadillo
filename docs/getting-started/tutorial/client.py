# client.py
import asyncio
from contextlib import suppress
import websockets


async def client(url: str):
    async with websockets.connect(url) as websocket:
        while True:
            message = input("> ")
            await websocket.send(message)
            response = await websocket.recv()
            print(response)


with suppress(KeyboardInterrupt):
    # 3.7+. See asyncio docs for <3.7 usage.
    asyncio.run(client("ws://localhost:8000/conversation"))
