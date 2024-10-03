import asyncio
import json
import threading

import websockets

clients = set()


async def websocket_server(websocket, path):
    global clients
    clients.add(websocket)
    print("Client connected")
    try:
        async for message in websocket:
            pass
    finally:
        clients.remove(websocket)


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
    loop.run_until_complete(send_to_all_clients(data))


async def send_to_all_clients(data):
    if clients:
        await asyncio.gather(*(client.send(data) for client in clients))


# Start the WebSocket server in a thread
server_thread = threading.Thread(target=run_websocket_server)
server_thread.daemon = True
server_thread.start()
print("WebSocket server started")
