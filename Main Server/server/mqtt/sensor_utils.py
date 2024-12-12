import json                    #Added by Sai
import time
import os
import csv
# from flask_mqtt import Mqtt
import paho.mqtt.client as mqtt

from server.config import Config 

# mqtt_client = Mqtt()
mqtt_client = mqtt.Client()

sensor_state = {"sensor_type": "", "sensor_id": "","partition_id": 0, "sensor_location": "", "reading": 0.0, "current_status": 0}

def SetSensorState(type, id,partID, location, reading, status):
    global sensor_state
    sensor_state["sensor_type"] = type
    sensor_state["sensor_id"] = id
    sensor_state["partition_id"] = partID
    sensor_state["sensor_location"] = location
    sensor_state["reading"] = reading
    sensor_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)
    #print(f"Received new sensor state: {sensor_state}")

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
        mqtt_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
        mqtt_client.subscribe("/sensor_temperature", qos=1)  # Subscribe to the location topic
        print("/sensor_temperature")
        mqtt_client.subscribe("/sensor_airquality", qos=1)  # Subscribe to the location topic
        print("/sensor_airquality")
        mqtt_client.subscribe("/sensor_humidity", qos=1)  # Subscribe to the location topic
        print("/sensor_humidity")
        mqtt_client.on_message = on_message  # Set the message handler
        mqtt_client.loop_start()  # Start the MQTT loop in a separate thread


def on_message(client, userdata, message):
    t = time.time()
    topic = message.topic
    payload = message.payload.decode()

    try:
        data = json.loads(payload) 
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for topic {topic}: {payload}")
        return

    # Default values for sensor state
    sensor_type = ""
    sensor_id = data.get("sensor_id", "unknown")
    partition_id = data.get("partition_id", 0)
    sensor_location = data.get("location", "unknown")
    reading = data.get("value", 0.0)
    status = data.get("status", 0) 

    
    if topic == "/sensor_temperature":
        sensor_type = "Temperature"
        reading = data.get("temperature", 0.0)
        status = 1  

    elif topic == "/sensor_airquality":
        sensor_type = "Air Quality"
        reading = data.get("air_quality", 0.0)
        status = 1  

    elif topic == "/sensor_humidity":
        sensor_type = "Humidity"
        reading = data.get("humidity", 0.0)
        status = 1  

    else:
        print(f"Unknown topic: {topic}")
        return

    
    SetSensorState(sensor_type, sensor_id, partition_id, sensor_location, reading, status)

    # Print updated sensor state
    print(f"Updated sensor state: {sensor_state}")

        
        


# def SendResponse(data, t2):
#     response_topic = f"{data["agv_id"]}/response"
#     response = data
#     response["t2"]= t2

#     t3 = time.time()
#     response["t3"]= t3

#     response = json.dumps(response)
#     mqtt_client.publish(response_topic, response, qos=data["qos"])
#     return

# def SaveToCSV(AGV_ID, interrupt_value,  t1, t2, t3, t4, filename):
#     # Check if file exists
#     file_exists = os.path.isfile(filename)

#     # Open CSV file in append mode
#     with open(filename, mode="a", newline='') as file:
#         writer = csv.writer(file)

#         # If file does not exist, write the header
#         if not file_exists:
#             writer.writerow(["AGV_ID", "interrupt_value", "t1", "t2", "t3", "t4"])  # Write the header

#         # Write the row with timestamps
#         writer.writerow([AGV_ID, interrupt_value, t1, t2, t3, t4])


