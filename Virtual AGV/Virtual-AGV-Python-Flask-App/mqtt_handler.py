import time
import datetime
import json
import threading

import paho.mqtt.client as mqtt

from utils import SaveCommunicationTime, SavePacketData

interrupt = 0  # Global interrupt variable
#goal = None  # Global goal variable
interrupt_lock = threading.Lock()
#goal_lock = threading.Lock()
agv_id = None
location_update_id = 0
task_end_update_id = 0
interrupt_response_id = 0

MQTT_BROKER = "localhost"
# MQTT_BROKER = "host.docker.internal"

MQTT_PORT = 1883
MQTT_LOCATION_TOPIC = "agv/location"
MQTT_TASK_END_TOPIC = "agv/task_complete"
MQTT_AGV_RESPONSE_TOPIC = "agv/response"
MQTT_GOAL_TOPIC = ""
MQTT_INTERRUPT_TOPIC = ""

mqtt_client = mqtt.Client()


def SetInterrupt(value):
    global interrupt
    with interrupt_lock:
        interrupt = value


def GetInterrupt():
    global interrupt
    with interrupt_lock:
        return interrupt


# def SetGoal(new_goal):
#     global goal
#     with goal_lock:
#         goal = new_goal


# def GetGoal():
#     global goal
#     with goal_lock:
#         return goal


def setTopic(AGV_ID):

    global agv_id
    agv_id = f"agv{AGV_ID}"
    global MQTT_INTERRUPT_TOPIC
    #global MQTT_GOAL_TOPIC
    global MQTT_RESPONSE_TOPIC
    #MQTT_GOAL_TOPIC = f"{agv_id}/goal"
    MQTT_INTERRUPT_TOPIC = f"{agv_id}/interrupt"
    MQTT_RESPONSE_TOPIC = f"{agv_id}/response"
    '''print(f"MQTT_LOCATION_TOPIC: {MQTT_LOCATION_TOPIC}")
    print(f"MQTT_GOAL_TOPIC: {MQTT_GOAL_TOPIC}")
    print(f"MQTT_INTERRUPT_TOPIC: {MQTT_INTERRUPT_TOPIC}")
    print(f"MQTT_RESPONSE_TOPIC: {MQTT_RESPONSE_TOPIC}")'''

def ConnectMQTT(AGV_ID):
    setTopic(AGV_ID)
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.subscribe(MQTT_INTERRUPT_TOPIC, qos=2)  # Subscribe to the interrupt topic
        #mqtt_client.subscribe(MQTT_GOAL_TOPIC, qos=2)  # Subscribe to the goal topic
        mqtt_client.subscribe(MQTT_RESPONSE_TOPIC, qos=2) 
        mqtt_client.on_message = on_message  # Set the message handler
        mqtt_client.loop_start()  # Start the MQTT loop in a separate thread
        '''print(f"Subscribed to MQTT topic '{MQTT_INTERRUPT_TOPIC}' for interrupts")
        print(f"Subscribed to MQTT topic '{MQTT_GOAL_TOPIC}' for goals")'''
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")


def on_message(client, userdata, message):
    try:
        t = time.time()
        data = json.loads(message.payload.decode())
        if message.topic == MQTT_INTERRUPT_TOPIC:
            print(f"Received message on topic '{message.topic}': {data}")

            interrupt_value = data.get("interrupt")
            recived_packet_id = data['id']
            SendResponse(data, t)

            SavePacketData(recived_packet_id, agv_id, "interrupt", "received_packets.csv")

            SetInterrupt(interrupt_value)

        #elif message.topic == MQTT_GOAL_TOPIC:
            # print(f"Received message on topic '{message.topic}': {data}")
            # SetGoal(data)
            # print(f"Received new goal: {goal}")
        
        elif message.topic == MQTT_RESPONSE_TOPIC:
            t1 = data["t1"]
            t2 = data["t2"]
            t3 = data["t3"]
            if data["topic"] == "agv/location":
                SaveCommunicationTime(agv_id, t1, t2, t3, t, "update_location.csv")
                SavePacketData(data["id"], agv_id, "location_update_response", "received_packets.csv")
            elif data["topic"] == "agv/task_complete":
                SaveCommunicationTime(agv_id, t1, t2, t3, t, "update_task_end.csv")
                SavePacketData(data["id"], agv_id, "task_end_update_response", "received_packets.csv")

    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}")


def UpdateCurrentLocation():
    from utils import agv_state
    packet_type = 5
    global location_update_id
    location_update_id += 1
    sent_packet_id = f"{agv_id}/{packet_type}/{location_update_id}"

    # Get the current time in a readable format
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Get the current time 
    t1 = time.time()

    location_data = {
        "id": sent_packet_id,
        "agv_id": f"agv{agv_state["agv_id"]}",
        "location": agv_state["current_location"],
        "segment": agv_state["current_segment"],
        "status": agv_state["current_status"],
        "timestamp": timestamp,
        "qos": 1,
        "t1": t1,
        "t2": t1, # Dummy value as in format of response from main server
        "t3": t1, # Dummy value as in format of response from main server
        "topic": "agv/location", # Dummy value as in format of response from main server

    }
    mqtt_client.publish(MQTT_LOCATION_TOPIC, json.dumps(location_data), qos=1)
    print(
        f"Published current location {location_data['location']} & status {agv_state["current_status"]} to MQTT topic '{MQTT_LOCATION_TOPIC} at{time.time()}"
    )
    SavePacketData(sent_packet_id, agv_id, "location_update", "sent_packets.csv")

def SendResponse(data, t2): 
    packet_type = 10
    global interrupt_response_id
    interrupt_response_id += 1
    sent_packet_id = f"{agv_id}/{packet_type}/{interrupt_response_id}"  
    
    response = data
    response["id"] = sent_packet_id
    response["t2"] = t2

    t3 = time.time()
    response["t3"] = t3

    response = json.dumps(response)
    mqtt_client.publish(MQTT_AGV_RESPONSE_TOPIC, response, qos=2)
    SavePacketData(sent_packet_id, agv_id, "interrupt_response", "sent_packets.csv")
    return

def EndTask(AGV_ID):
    # ---------- print("Inside EndTask")
    try:
        packet_type = 7
        global task_end_update_id
        task_end_update_id += 1
        sent_packet_id = f"{agv_id}/{packet_type}/{task_end_update_id}"
        # Get the current time in a readable format
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Get the current time in a readable format
        t1 = time.time()

        data = {
                "id": sent_packet_id,
                "agv_id": f"agv{AGV_ID}", 
                "timestamp": timestamp,
                "qos": 2,
                "topic": "agv/task_complete",
                "t1": t1,
                "t2": t1, # Dummy value as in format of response from main server
                "t3": t1, # Dummy value as in format of response from main server
                }
        mqtt_client.publish(MQTT_TASK_END_TOPIC, json.dumps(data), qos=2)
        SavePacketData(sent_packet_id, agv_id, "task_end_update", "sent_packets.csv")

    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")
