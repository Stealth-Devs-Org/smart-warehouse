import json

from flask_mqtt import Mqtt

mqtt_client = Mqtt()


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        mqtt_client.subscribe("agv_location")
        print("Subscribed to agv_location")
    else:
        print("Bad connection. Code:", rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):

    topic = message.topic
    payload = message.payload.decode()
    data = json.loads(payload)

    match topic:
        case "agv_location":
            update_agv_location(data)

        case "Python":
            print("You can become a Data Scientist")

        case "PHP":
            print("You can become a backend developer")

        case "Solidity":
            print("You can become a Blockchain developer")

        case "Java":
            print("You can become a mobile app developer")
        case _:
            print("The language doesn't matter, what matters is solving problems.")


from server.agv.col_avoid import update_agv_location
