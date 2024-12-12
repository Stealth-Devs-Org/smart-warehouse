import threading
import time

from flask_socketio import SocketIO, emit

socketio = SocketIO()


@socketio.on("connected")
def handle_my_custom_event(json):
    print("received json: " + str(json))


# def emit_to_webpage(agvs_data, permanent_obstacles):
#     dto = {"agvs_data": agvs_data, "permanent_obstacles": permanent_obstacles}
#     socketio.emit("agv_location", dto)


# def emit_data_periodically(interval, agvs_data, permanent_obstacles):
#     while True:
#         emit_to_webpage(agvs_data, permanent_obstacles)
#         time.sleep(interval)


def emit_data_periodically(interval, sensor_data):
    while True:
        emit_to_webpage(sensor_data)
        time.sleep(interval)

def start_emission_thread(interval):
    from server.agv.col_avoid import agvs_data
    from server.agv.keep_alive import permanent_obstacles

    emission_thread = threading.Thread(
        target=emit_data_periodically, args=(interval, agvs_data, permanent_obstacles)
    )
    emission_thread.daemon = True
    emission_thread.start()
