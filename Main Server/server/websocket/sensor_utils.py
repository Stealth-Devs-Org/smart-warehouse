import threading
import time

from flask_socketio import SocketIO, emit

socketio = SocketIO()


@socketio.on("connected")
def handle_my_custom_event(json):
    print("received json: " + str(json))


def emit_to_webpage(sensor_data):
    dto = {"sensor_data": sensor_data}
    socketio.emit("agv_location", dto)


def emit_data_periodically(interval, sensor_data, permanent_obstacles):
    while True:
        emit_to_webpage(sensor_data, permanent_obstacles)
        time.sleep(interval)


def emit_data_periodically(interval, sensor_data):
    while True:
        emit_to_webpage(sensor_data)
        time.sleep(interval)

def start_emission_thread(interval):
    from server.agv.col_avoid import sensor_data
    

    emission_thread = threading.Thread(
        target=emit_data_periodically, args=(interval, sensor_data)
    )
    emission_thread.daemon = True
    emission_thread.start()
