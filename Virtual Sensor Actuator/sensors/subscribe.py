

# TEST CODE TO SUBSCRIBE TO TOPICS

import paho.mqtt.client as mqtt

BROKER = "localhost"  
PORT = 1883
TOPIC1 = "/sensor_temperature"
TOPIC2 = "/sensor_airquality"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC1)
        client.subscribe(TOPIC2)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    #print(f"ClientID={client} Topic={msg.topic} Message={payload}")
    print(f"Received :  {msg.topic}: {payload}")

def main():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
