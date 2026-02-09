import asyncio
import websockets
import json
import random
from datetime import datetime


async def agv_handler(websocket, path):
    print(f"Client connected on path: {path}")
    await websocket.send("Welcome to the AGV server")

    y = 0  

    while True:
        agv = {
            "agv_id": 1,
            "location": [15, y],
            "segment": random.randint(0, 4),
            "status": random.randint(0, 3),  # 0: idle, 1: moving, 2: loading, 3: unloading
            "timestamp": datetime.utcnow().isoformat()
        }
        y += 1  # increment y to test straight line..........
        agv_data = json.dumps(agv)
        await websocket.send(agv_data)  

        await asyncio.sleep(1)  


start_server = websockets.serve(agv_handler, "0.0.0.0", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server is running on ws://0.0.0.0:8080")
asyncio.get_event_loop().run_forever()
