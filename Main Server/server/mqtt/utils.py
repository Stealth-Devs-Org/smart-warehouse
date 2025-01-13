import json

# from flask_mqtt import Mqtt
import paho.mqtt.client as mqtt

from server.config import Config

# mqtt_client = Mqtt()
mqtt_client = mqtt.Client()


# @mqtt_client.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected successfully")
#         mqtt_client.subscribe("agv/location", qos=1)
#         print("Subscribed to agv/location")
#         mqtt_client.subscribe("agv/task_complete", qos=2)
#         print("Subscribed to agv/task_complete")
#     else:
#         print("Bad connection. Code:", rc)


# @mqtt_client.on_message()
# def handle_mqtt_message(client, userdata, message):

#     topic = message.topic
#     payload = message.payload.decode()
#     data = json.loads(payload)

#     if topic == "agv/location":
#         from server.agv.col_avoid import update_agv_location

#         update_agv_location(data)

#     elif topic == "agv/task_complete":
#         from server.agv.scheduler import task_complete

#         task_complete(data)


def ConnectMQTT():
    try:
        mqtt_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
        mqtt_client.subscribe("agv/location", qos=1)  # Subscribe to the location topic
        print("Subscribed to agv/location")
        mqtt_client.subscribe("agv/task_complete", qos=2)  # Subscribe to the task complete topic
        print("Subscribed to agv/task_complete")
        mqtt_client.on_message = on_message  # Set the message handler
        mqtt_client.loop_start()  # Start the MQTT loop in a separate thread
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")


def on_message(client, userdata, message):
    try:
        topic = message.topic
        payload = message.payload.decode()
        data = json.loads(payload)
        if topic == "agv/location":
            from server.agv.col_avoid import update_agv_location

            update_agv_location(data)

        elif topic == "agv/task_complete":
            from server.agv.scheduler import task_complete

            task_complete(data)
    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}")
