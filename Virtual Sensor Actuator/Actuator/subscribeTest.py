

# to test subscribe.py, run the following command in the terminal



import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "/actuator_control_humidity"  # The same topic to subscribe to

def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with result code {rc}")
    client.subscribe(TOPIC)  # Subscribe to the topic when connected

def on_message(client, userdata, msg):
    
    payload = json.loads(msg.payload)  # Parse the incoming JSON message
    print(f"Received message on topic {msg.topic}: {json.dumps(payload, indent=4)}")

        

# Set up MQTT client
mqtt_client = mqtt.Client()

# Assign event callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to the MQTT broker
mqtt_client.connect(BROKER, PORT, 60)

# Start the MQTT loop
mqtt_client.loop_forever()
