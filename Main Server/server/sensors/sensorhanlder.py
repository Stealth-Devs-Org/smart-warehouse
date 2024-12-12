import datetime
import json
import threading
import time

from mqtt.sensor_utils import SetSensorState
from mqtt.sensor_utils import sensor_state


from server.websocket.websocket import (
    send_sensor_data_through_websocket,
    send_through_websocket,
)


def send_sensor_data_websocket():
    while True:
        for sensor_type, sensor_data in sensor_state.items():
            send_sensor_data_through_websocket(sensor_type, sensor_data)
        time.sleep(1)


    



