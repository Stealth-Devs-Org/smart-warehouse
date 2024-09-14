from server import create_app
from server.websocket.utils import socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app)
