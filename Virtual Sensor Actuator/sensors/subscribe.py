import paho.mqtt.client as mqtt

# MQTT broker configuration
BROKER = "localhost"  # Replace with the MQTT broker address
PORT = 1883
TOPIC = "/sensor"

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        # Subscribe to the /sensor topic after connecting
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    # msg.topic is the topic where the message was published
    # msg.payload contains the actual message (in bytes)
    payload = msg.payload.decode('utf-8')
    print(f"Received message from {msg.topic}: {payload}")

def main():
    # Initialize the MQTT client
    client = mqtt.Client()

    # Attach the callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT broker
    client.connect(BROKER, PORT, 60)

    # Blocking call to process network traffic and dispatch callbacks
    client.loop_forever()

if __name__ == "__main__":
    main()
