import datetime
import json
import threading
import time


from server.mqtt.sensor_utils import sensor_state, ConnectMQTT

ConnectMQTT()


from server.websocket.websocket import (
    send_sensor_data_through_websocket
)


def send_sensor_data_websocket():
    while True:
        send_sensor_data_through_websocket(sensor_state)
        time.sleep(1)



