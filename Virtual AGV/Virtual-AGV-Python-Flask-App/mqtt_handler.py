import json
import paho.mqtt.client as mqtt
import threading
import datetime

interrupt = 0  # Global interrupt variable
interrupt_lock = threading.Lock()

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

mqtt_client = mqtt.Client()

def SetInterrupt(value):
    global interrupt
    with interrupt_lock:
        interrupt = value

def GetInterrupt():
    global interrupt
    with interrupt_lock:
        return interrupt

def setTopic(AGV_ID):
    global MQTT_LOCATION_TOPIC
    global MQTT_INTERRUPT_TOPIC
    MQTT_LOCATION_TOPIC = f"agv/{AGV_ID}/location"
    print(f"MQTT_LOCATION_TOPIC: {MQTT_LOCATION_TOPIC}")
    MQTT_INTERRUPT_TOPIC = f"agv/{AGV_ID}/interrupt"
    print(f"MQTT_INTERRUPT_TOPIC: {MQTT_INTERRUPT_TOPIC}")

def ConnectMQTT(AGV_ID):
    setTopic(AGV_ID)
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.subscribe(MQTT_INTERRUPT_TOPIC)  # Subscribe to the interrupt topic
        mqtt_client.on_message = on_message  # Set the message handler
        mqtt_client.loop_start()  # Start the MQTT loop in a separate thread
        print(f"Subscribed to MQTT topic '{MQTT_INTERRUPT_TOPIC}' for interrupts")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")

def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())
        interrupt_value = data.get('interrupt')
        if interrupt_value == '1':
            SetInterrupt(0)
            print("Received 'Resume' interrupt. Resuming AGV.")
        elif interrupt_value == '2':
            SetInterrupt(1)
            print("Received 'Stop' interrupt. Stopping AGV.")
        else:
            SetInterrupt(interrupt_value)
            print("Received 'Recalculate path' interrupt. Interrupt value:", interrupt_value)
    except json.JSONDecodeError as e:
        print(f"Error decoding interrupt message: {e}")

def UpdateCurrentLocation(current_segment):
    try:
        # Get the current time in a readable format
        timestamp = datetime.datetime.now().isoformat()
        if len(current_segment) == 1:
            remaining_path = []
        else:
            remaining_path = current_segment[1:]

        location_data = {
            "current_location": current_segment[0],
            "remaining_segment": remaining_path,
            "timestamp": timestamp
            }
        mqtt_client.publish(MQTT_LOCATION_TOPIC, json.dumps(location_data))
        print(f"Published current location {current_segment[0]} to MQTT topic '{MQTT_LOCATION_TOPIC}'")
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")
