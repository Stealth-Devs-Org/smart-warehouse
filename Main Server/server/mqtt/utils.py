import json

from flask_mqtt import Mqtt

mqtt_client = Mqtt()


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        mqtt_client.subscribe("agv_location", qos=1)
        print("Subscribed to agv_location")
    else:
        print("Bad connection. Code:", rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):

    topic = message.topic
    payload = message.payload.decode()
    data = json.loads(payload)

    if topic == "agv_location":
        from server.agv.col_avoid import update_agv_location

        update_agv_location(data)
