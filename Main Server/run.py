from server import create_app
from server.agv.col_avoid import run_collision_avoidance
from server.agv.scheduler import run_task_scheduler
from server.websocket.utils import socketio

app = create_app()

if __name__ == "__main__":
    run_task_scheduler(5)  # Run the task scheduler every {arg} seconds
    # run_collision_avoidance(0.25)  # Run the collision avoidance every {arg} second
    socketio.run(app, host="0.0.0.0", port=5000)
