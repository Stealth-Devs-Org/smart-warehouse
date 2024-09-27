import json
import paho.mqtt.client as mqtt
import threading
import datetime

interrupt = 0  # Global interrupt variable
goal = None  # Global goal variable
interrupt_lock = threading.Lock()
goal_lock = threading.Lock()

MQTT_BROKER = "host.docker.internal"
MQTT_PORT = 1883
MQTT_LOCATION_TOPIC = "agv/location"
MQTT_TASK_END_TOPIC = "agv/task_complete"

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


def ConnectMQTT(AGV_ID):
    setTopic(AGV_ID)
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.subscribe(MQTT_INTERRUPT_TOPIC)  # Subscribe to the interrupt topic
        mqtt_client.subscribe(MQTT_GOAL_TOPIC)  # Subscribe to the goal topic
        mqtt_client.on_message = on_message  # Set the message handler
        mqtt_client.loop_start()  # Start the MQTT loop in a separate thread
        print(f"Subscribed to MQTT topic '{MQTT_INTERRUPT_TOPIC}' for interrupts")
        print(f"Subscribed to MQTT topic '{MQTT_GOAL_TOPIC}' for goals")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")




def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())
        if message.topic == MQTT_INTERRUPT_TOPIC:
            interrupt_value = data.get('interrupt')
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


def UpdateCurrentLocation(current_segment,AGV_ID,status):
    try:
        # Get the current time in a readable format
        timestamp = datetime.datetime.now().isoformat()
        

        location_data = {
            "agv_id": f"agv{AGV_ID}",
            "location": current_segment[0],
            "segment": current_segment,
            "status": status, # 0: idle, 1: moving forward, 2: Loading, 3: Unloading, 4: Charging, 5:Turning Right, 6:Turning Left, 7:Turning Back, 8:Turning Completed, 9:Reverse  
            "timestamp": timestamp
            }
        mqtt_client.publish(MQTT_LOCATION_TOPIC, json.dumps(location_data))
        print(f"Published current location {current_segment[0]} to MQTT topic '{MQTT_LOCATION_TOPIC}'")
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")

def EndTask(AGV_ID):
    try:
        # Get the current time in a readable format
        timestamp = datetime.datetime.now().isoformat()
        
        data = {
            "agv_id": f"agv{AGV_ID}",
            "timestamp": timestamp
            }
        mqtt_client.publish(MQTT_TASK_END_TOPIC, json.dumps(data))
        
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")


