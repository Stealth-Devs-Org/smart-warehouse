import datetime
import json
import os
import threading
import time

import paho.mqtt.client as mqtt
import yaml

# Read configuration file
config_path = os.getenv("CONFIG_PATH", "config.yaml")
instance_id = int(os.getenv("INSTANCE_ID", "0"))

# Load configurations
def read_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

config = read_config(config_path)["instances"][instance_id]

AGV_ID = config["AGV_ID"]
MQTT_BROKER = "localhost"
# MQTT_BROKER = "host.docker.internal"
MQTT_PORT = 1883
MQTT_LOCATION_TOPIC = "agv/location"
MQTT_TASK_END_TOPIC = "agv/task_complete"
MQTT_GOAL_TOPIC = f"agv{AGV_ID}/goal"
MQTT_INTERRUPT_TOPIC = f"agv{AGV_ID}/interrupt"

mqtt_client = mqtt.Client()

goal = None  # Global goal variable



def GetGoal():
    return goal


def SetGoal(goal_local):
    global goal
    goal = goal_local
    
    
def on_message(client, userdata, message):
    
    from app import StartTask, StopTask
    
    speed = config["speed"]  # Speed of the AGV
    cell_distance = config["cell_distance"]  # cell_distance between two cells
    
    try:
        data = json.loads(message.payload.decode())
        if message.topic == MQTT_INTERRUPT_TOPIC:
            interrupt_value = data.get("interrupt")
            if interrupt_value == 1:
                # TODO Code to stop navigation thread
                print("Received 'Stop' interrupt. Stopping AGV.")
                StopTask()
                cell_time = cell_distance / speed
                time.sleep(cell_time * 3)
                
            else:
                # TODO Code to stop navigation thread and start with recalculated path
                print("Received 'Recalculate path' interrupt. Interrupt value:", interrupt_value)
                StopTask()

        elif message.topic == MQTT_GOAL_TOPIC:
            global goal
            goal = data
            print(f"Received new goal: {goal}")
            
        StartTask()

    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}")
        
    
def ConnectMQTT():
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.subscribe(MQTT_INTERRUPT_TOPIC, qos=2)  # Subscribe to the interrupt topic
        mqtt_client.subscribe(MQTT_GOAL_TOPIC, qos=2)  # Subscribe to the goal topic
        mqtt_client.on_message = on_message  # Set the message handler
        mqtt_client.loop_start()  # Start the MQTT loop in a separate thread
        print(f"Subscribed to MQTT topic '{MQTT_INTERRUPT_TOPIC}' for interrupts")
        print(f"Subscribed to MQTT topic '{MQTT_GOAL_TOPIC}' for goals")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")

ConnectMQTT()


def UpdateCurrentLocation():
    with open("agv_status.json", "r") as f:
        agv_status = json.load(f)
    
    try:
        # Get the current time in a readable format
        timestamp = datetime.datetime.now().isoformat()

        location_data = {
            "agv_id": f"agv{AGV_ID}",
            "location": agv_status["location"],
            "segment": agv_status["segment"],
            "status": agv_status["status"],
            "timestamp": timestamp,
        }
        mqtt_client.publish(MQTT_LOCATION_TOPIC, json.dumps(location_data), qos=2)
        print(
            f"Published current location {agv_status["location"]} to MQTT topic '{MQTT_LOCATION_TOPIC}'"
        )
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")



def EndTask():
    print("Inside EndTask")
    try:
        # Get the current time in a readable format
        timestamp = datetime.datetime.now().isoformat()

        data = {"agv_id": f"agv{AGV_ID}", "timestamp": timestamp}
        mqtt_client.publish(MQTT_TASK_END_TOPIC, json.dumps(data), qos=2)

    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")
        
        

