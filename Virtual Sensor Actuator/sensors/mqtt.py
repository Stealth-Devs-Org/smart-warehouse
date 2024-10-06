import datetime
import json
import threading

import paho.mqtt.client as mqtt

from utils import Get_values_from_agv_json
from TemperatureSensor import sensor_state

interrupt = 0  # Global interrupt variable
goal = None  # Global goal variable
interrupt_lock = threading.Lock()
goal_lock = threading.Lock()

MQTT_BROKER = "localhost"
# MQTT_BROKER = "host.docker.internal"

MQTT_PORT = 1883
MQTT_LOCATION_TOPIC = "agv/location"
MQTT_TASK_END_TOPIC = "agv/task_complete"
MQTT_SENSOR_TOPIC = "Sensor/Temperature"        ################################################################### SAIRISAN
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


def SetGoal(new_goal):
    global goal
    with goal_lock:
        goal = new_goal


def GetGoal():
    global goal
    with goal_lock:
        return goal


def setTopic(AGV_ID):

    global MQTT_INTERRUPT_TOPIC
    global MQTT_GOAL_TOPIC
    MQTT_GOAL_TOPIC = f"agv{AGV_ID}/goal"
    MQTT_INTERRUPT_TOPIC = f"agv{AGV_ID}/interrupt"
    print(f"MQTT_LOCATION_TOPIC: {MQTT_LOCATION_TOPIC}")
    print(f"MQTT_GOAL_TOPIC: {MQTT_GOAL_TOPIC}")
    print(f"MQTT_INTERRUPT_TOPIC: {MQTT_INTERRUPT_TOPIC}")

###############################################################################
def SetTopic(SensorID):
    global MQTT_SENSOR_TOPIC
    MQTT_SENSOR_TOPIC = f"Sensor/{SensorID}"
    print(f"MQTT_SENSOR_TOPIC: {MQTT_SENSOR_TOPIC}")

###############################################################################


def ConnectMQTT(AGV_ID):
    setTopic(AGV_ID)
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


def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())
        print(f"Received message on topic '{message.topic}': {data}")
        if message.topic == MQTT_INTERRUPT_TOPIC:
            interrupt_value = data.get("interrupt")
            if interrupt_value == 1:
                SetInterrupt(1)
                print("Received 'Stop' interrupt. Stopping AGV.")
            else:
                SetInterrupt(interrupt_value)
                print("Received 'Recalculate path' interrupt. Interrupt value:", interrupt_value)

        elif message.topic == MQTT_GOAL_TOPIC:
            SetGoal(data)
            print(f"Received new goal: {goal}")

    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}")


def UpdateCurrentLocation():
    from utils import agv_state

    # Get the current time in a readable format
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    location_data = {
        "agv_id": f"agv{agv_state["agv_id"]}",
        "location": agv_state["current_location"],
        "segment": agv_state["current_segment"],
        "status": agv_state["current_status"],
        "timestamp": timestamp,
    }
    mqtt_client.publish(MQTT_LOCATION_TOPIC, json.dumps(location_data), qos=1)
    print(
        f"Published current location {location_data['location']} & status {agv_state["current_status"]} to MQTT topic '{MQTT_LOCATION_TOPIC}'"
    )

############################################################################################
def UpdateSensorReadings():
    # Get the current time in a readable format
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    sensor_data = {
        "sensor_type": sensor_state["sensor_type"],
        "sensor_id": f"sensor{sensor_state["sensor_id"]}",
        "location": sensor_state["sensor_location"],
        "reading": sensor_state["reading"],
        "status": sensor_state["current_status"],
        "timestamp": timestamp,
    }
    mqtt_client.publish(MQTT_SENSOR_TOPIC, json.dumps(sensor_data), qos=1)
    print(
         f"Published current location {sensor_data['location']} & reading {sensor_state["reading"]} to MQTT topic '{MQTT_SENSOR_TOPIC}'"
     )


############################################################################################



def EndTask(AGV_ID):
    print("Inside EndTask")
    try:
        # Get the current time in a readable format
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        data = {"agv_id": f"agv{AGV_ID}", "timestamp": timestamp}
        mqtt_client.publish(MQTT_TASK_END_TOPIC, json.dumps(data), qos=2)

    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")