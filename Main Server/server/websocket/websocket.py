import asyncio
import json
import threading

import websockets

clients = {}


async def websocket_server(websocket, path):
    if path not in clients:
        clients[path] = set()
    clients[path].add(websocket)
    print(f"Client connected to {path}")
    try:
        async for message in websocket:
            pass
    finally:
        clients[path].remove(websocket)
        if not clients[path]:
            del clients[path]


def run_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(websocket_server, "localhost", 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()


def send_through_websocket(data):
    data = json.dumps(data)
    # print("Received external data:", data)

    # Send to all WebSocket clients asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_all_clients(data, "/"))


def send_agv_data_through_websocket(data):
    data = json.dumps(data)
    # print("Received external data:", data)

    # Send to all WebSocket clients asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_all_clients(data, "/agv"))


def send_obstacle_data_through_websocket(data):
    data = json.dumps(data)
    # print("Received external data:", data)

    # Send to all WebSocket clients asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_all_clients(data, "/obstacle"))


def send_sensor_data_through_websocket(data):
    data = json.dumps(data)
    # print("Received external data:", data)

    # Send to all WebSocket clients asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_all_clients(data, "/sensor"))


def send_actuator_data_through_websocket(data):
    data = json.dumps(data)
    # print("Received external data:", data)

    # Send to all WebSocket clients asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_all_clients(data, "/actuator"))


async def send_to_all_clients(data, path):
    if path in clients and clients[path]:
        await asyncio.gather(*(client.send(data) for client in clients[path]))
        print(f"Sent data to {len(clients[path])} clients")


# Start the WebSocket server in a thread
server_thread = threading.Thread(target=run_websocket_server)
server_thread.daemon = True
server_thread.start()
print("WebSocket server started")
