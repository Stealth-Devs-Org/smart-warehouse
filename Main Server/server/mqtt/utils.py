import json
import time
import os
import csv
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
        mqtt_client.subscribe("agv/response", qos=2)
        mqtt_client.on_message = on_message  # Set the message handler
        mqtt_client.loop_start()  # Start the MQTT loop in a separate thread
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")


def on_message(client, userdata, message):
    try:
        t = time.time()
        topic = message.topic
        payload = message.payload.decode()
        data = json.loads(payload)
        t1 = data["t1"]
        SendResponse(data["agv_id"], t1, t, topic)
        
        if topic == "agv/location":
            from server.agv.col_avoid import update_agv_location

            update_agv_location(data)

        elif topic == "agv/task_complete":
            from server.agv.scheduler import task_complete

            task_complete(data)

        elif topic == "agv/response":
            print(data,"***********************************************")
            t2 = data["t2"]
            t3 = data["t3"]
            SaveToCSV(data["agv_id"], data["interrupt_value"], t1, t2, t3, t, "interrupt_response.csv")

    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}")

def SendResponse(AGV_ID, t1, t2, topic):
    response_topic = f"{AGV_ID}/response"
    
    t3 = time.time()
    response = {
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "topic": topic
    }

    response = json.dumps(response)
    mqtt_client.publish(response_topic, response, qos=2)
    return

def SaveToCSV(AGV_ID, interrupt_value,  t1, t2, t3, t4, filename):
    # Check if file exists
    file_exists = os.path.isfile(filename)

    # Open CSV file in append mode
    with open(filename, mode="a", newline='') as file:
        writer = csv.writer(file)

        # If file does not exist, write the header
        if not file_exists:
            writer.writerow(["AGV_ID", "interrupt_value", "t1", "t2", "t3", "t4"])  # Write the header

        # Write the row with timestamps
        writer.writerow([AGV_ID, interrupt_value, t1, t2, t3, t4])




