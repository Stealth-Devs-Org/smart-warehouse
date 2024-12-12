import json                    #Added by Sai
import time

# from flask_mqtt import Mqtt
import paho.mqtt.client as mqtt

from server.config import Config 

# mqtt_client = Mqtt()
mqtt_client = mqtt.Client()

sensor_state = {"sensor_type": "", "sensor_id": "","partition_id": 0, "sensor_location": "", "reading": 0.0, "current_status": 0}

# def SetSensorState(type, id,partID, location, reading, status):
#     global sensor_state
#     sensor_state["sensor_type"] = type
#     sensor_state["sensor_id"] = id
#     sensor_state["partition_id"] = partID
#     sensor_state["sensor_location"] = location
#     sensor_state["reading"] = reading
#     sensor_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)

def ConnectMQTT():
        mqtt_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
        mqtt_client.subscribe("/sensor_temperature", qos=1)  # Subscribe to the location topic
        print("subscribed to sensor_temperature")
        mqtt_client.subscribe("/sensor_airquality", qos=1)  # Subscribe to the location topic
        print("subscribed to sensor_airquality")
        mqtt_client.subscribe("/sensor_humidity", qos=1)  # Subscribe to the location topic
        print("subscribed to sensor_humidity")
        mqtt_client.on_message = on_message  # Set the message handler
        mqtt_client.loop_start()  # Start the MQTT loop in a separate thread


def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode()

    try:
        data = json.loads(payload) 
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for topic {topic}: {payload}")
        return

    # Default values for sensor state
    sensor_state.update({
        "sensor_type": "",  # This will be set based on the topic
        "sensor_id": data.get("sensor_id", "unknown"),
        "partition_id": data.get("partition_id", 0),
        "sensor_location": data.get("sensor_location", "unknown"),
        "reading": 0.0,  # Placeholder, will be updated below
        "current_status": 0  # Placeholder, will be updated below
    })

    if topic == "/sensor_temperature":
        sensor_state["sensor_type"] = "Temperature"
        sensor_state["sensor_id"] = data.get("sensor_id")
        sensor_state["partition_id"] = data.get("partition_id")
        sensor_state["sensor_location"] = data.get("sensor_location")
        sensor_state["reading"] = data.get("reading")
        sensor_state["current_status"] = data.get("current_status")

    elif topic == "/sensor_airquality":
        sensor_state["sensor_type"] = "AirQuality"
        sensor_state["sensor_id"] = data.get("sensor_id")
        sensor_state["partition_id"] = data.get("partition_id")
        sensor_state["sensor_location"] = data.get("sensor_location")
        sensor_state["reading"] = data.get("reading")
        sensor_state["current_status"] = data.get("current_status")
        

    elif topic == "/sensor_humidity":
        sensor_state["sensor_type"] = "Humidity"
        sensor_state["sensor_id"] = data.get("sensor_id")
        sensor_state["partition_id"] = data.get("partition_id")
        sensor_state["sensor_location"] = data.get("sensor_location")
        sensor_state["reading"] = data.get("reading")
        sensor_state["current_status"] = data.get("current_status")


    else:
        print(f"Unknown topic: {topic}")
        return

  

    # Print updated sensor state
    #print(f"Updated sensor state: {sensor_state}")



