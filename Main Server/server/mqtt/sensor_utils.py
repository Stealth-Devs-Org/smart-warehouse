import json
import time
import paho.mqtt.client as mqtt
import logging
import os
import csv
from server.config import Config
from server.websocket.websocket import send_sensor_data_through_websocket

# Initialize dictionaries for storing sensor data with 7 partitions
all_Sensor_Temperature_data = [{} for _ in range(7)]  # 7 partitions
all_Sensor_AirQuality_data = [{} for _ in range(7)]
all_Sensor_Humidity_data = [{} for _ in range(7)]
all_Sensor_Smoke_data = [{} for _ in range(7)]

mqtt_client = mqtt.Client()

TOPIC = "/sensor_timestamps"

logging.basicConfig(level=logging.INFO)


def ConnectMQTT():
    mqtt_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
    mqtt_client.subscribe("/sensor_temperature", qos=1)
    mqtt_client.subscribe("/sensor_air_quality", qos=1)
    mqtt_client.subscribe("/sensor_humidity", qos=1)
    mqtt_client.subscribe("/temperature_control_timestamps", qos=1)
    mqtt_client.subscribe("/humidity_control_timestamps", qos=1)
    mqtt_client.subscribe("/airquality_control_timestamps", qos=1)
    mqtt_client.subscribe("/sensor_smoke", qos=1)

    
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()
    logging.info("MQTT connected and subscribed.")


def on_message(client, userdata, message):
    t = time.time()
    topic = message.topic
    payload = message.payload.decode()
    print(f"Received message on topic {topic}: {payload}")
    

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON received on topic {topic}: {payload}")
        return

    if topic == "/sensor_temperature" or topic == "/sensor_air_quality" or topic == "/sensor_humidity" or topic == "/sensor_smoke":
        data["t2"] = t
        t3 = time.time()
        data["t3"] = t3
        # Publish the message to the timestamp topic
        mqtt_client.publish(TOPIC, json.dumps(data), qos=1)

        # Send sensor data through WebSocket
        send_sensor_data_through_websocket(data, topic)


        partition_id = data.get("partition_id", -1)
        if partition_id < 0 or partition_id >= 7:
            logging.error(f"Invalid partition_id: {partition_id} in topic {topic}")
            return


        if topic == "/sensor_temperature":
            all_Sensor_Temperature_data[partition_id][data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
            write_to_file("all_Sensor_Temperature_data.json", all_Sensor_Temperature_data)
        elif topic == "/sensor_air_quality":
            all_Sensor_AirQuality_data[partition_id][data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
            write_to_file("all_Sensor_AirQuality_data.json", all_Sensor_AirQuality_data)
        elif topic == "/sensor_humidity":
            all_Sensor_Humidity_data[partition_id][data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
            write_to_file("all_Sensor_Humidity_data.json", all_Sensor_Humidity_data)
        elif topic == "/sensor_smoke":
            all_Sensor_Smoke_data[partition_id][data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
            write_to_file("all_Sensor_Smoke_data.json", all_Sensor_Smoke_data)
        else:
            logging.error(f"Unknown topic: {topic}")
            return
        
    elif topic == "/temperature_control_timestamps" or topic == "/humidity_control_timestamps" or topic == "/airquality_control_timestamps":
        type = topic.split("_")[0][1:]  # Extract the type from the topic
        t1 = data["t1"]
        t2 = data["t2"]
        t3 = data["t3"]
        t4 = t
        SaveActuatorTimestampsToCSV(type, t1, t2, t3, t4, "actuator_control_temperature.csv")

    
    
    

    #logging.info(f"Updated data for {topic}: {data}")


def write_to_file(filename, data):
    try:
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        logging.error(f"Error writing to {filename}: {e}")

def SaveActuatorTimestampsToCSV(type, t1, t2, t3, t4, filename):
    # Check if file exists
    file_exists = os.path.isfile(filename)

    # Open CSV file in append mode
    with open(filename, mode="a", newline='') as file:
        writer = csv.writer(file)

        # If file does not exist, write the header
        if not file_exists:
            writer.writerow(["ActuatorType", "t1", "t2", "t3", "t4"])  # Write the header
        writer.writerow([type, t1, t2, t3, t4])

# Main function to start the script
if __name__ == "__main__":
    ConnectMQTT()
    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        logging.info("MQTT connection stopped.")
