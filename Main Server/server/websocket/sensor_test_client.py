# import asyncio
# import websockets


# async def listen_to_sensor(uri):
#     try:
#         async with websockets.connect(uri) as websocket:
#             print(f"Connected to {uri}")
#             while True:
#                 message = await websocket.recv()
#                 print(f"Received from {uri}: {message}")
#     except websockets.exceptions.ConnectionClosedError as e:
#         print(f"Connection to {uri} closed: {e}")
#     except Exception as e:
#         print(f"Error connecting to {uri}: {e}")


# async def main():
#     sensor_uris = [
#         "ws://localhost:8765/sensor_temperature",
#         "ws://localhost:8765/sensor_airquality",
#         "ws://localhost:8765/sensor_humidity",
#     ]

#     # Create tasks for each WebSocket connection
#     tasks = [listen_to_sensor(uri) for uri in sensor_uris]

#     # Run all tasks concurrently
#     await asyncio.gather(*tasks)


# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio

import websockets


async def client():
    uri = "ws://localhost:8765/sensor"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")


asyncio.get_event_loop().run_until_complete(client())
