from server import create_app
from server.agv.scheduler import run_task_scheduler
from server.websocket.utils import socketio

app = create_app()

if __name__ == "__main__":
    run_task_scheduler(5)  # Run the task scheduler every 5 seconds
    socketio.run(app)
