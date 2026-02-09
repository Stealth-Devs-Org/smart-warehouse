import asyncio

import websockets


async def client():
    # uri = "ws://localhost:8765/agv"
    uri = "ws://192.168.43.177:8765/agv"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")


asyncio.get_event_loop().run_until_complete(client())
