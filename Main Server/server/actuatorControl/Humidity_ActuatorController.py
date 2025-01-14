import json
import paho.mqtt.client as mqtt
import time
import threading

BROKER = "localhost"
PORT = 1883
TOPIC = "/actuator_control_humidity"

desired_warehouse_humidity_values = [60.0, 65.0, 70.0, 65.0, 55.0, 57.0, 80.0]
threshold = 1.0  # Threshold for "off" condition
filename = 'all_Sensor_Humidity_data.json'

mqtt_client = mqtt.Client()


def calculate_averages_from_file(filename):
    try:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
    except Exception as e:
        print(f"Error reading the file {filename}: {e}")
        return None

    partition_averages = {}
    for i, partition_data in enumerate(data):
        partition_key = f"part{i}"
        values = list(partition_data.values())
        if values:  
            average = sum(values) / len(values)
        else:
            average = 0.0  
        partition_averages[partition_key] = average

    return partition_averages


def determine_actuator_command(current_humidity, desired_humidity):
    if abs(desired_humidity - current_humidity) < threshold:
        return "off"
    elif desired_humidity > current_humidity:
        return "raise"
    else:
        return "reduce"


def send_to_mqtt(commands):
    payload = json.dumps(commands)
    mqtt_client.publish(TOPIC, payload)
    print(f"Published to {TOPIC}: {payload}")


def run_actuator_control():
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()

    while True:
        partition_averages = calculate_averages_from_file(filename)

        if partition_averages:
            actuator_commands = {}
            for i, avg_humidity in partition_averages.items():
                part_index = int(i.replace('part', ''))
                desired_humidity = desired_warehouse_humidity_values[part_index]
                actuator_command = determine_actuator_command(avg_humidity, desired_humidity)
                actuator_commands[f"{i}_actuator"] = actuator_command
            
            send_to_mqtt(actuator_commands)
        
        time.sleep(1)  # 1-second interval

# Start the actuator control in a separate thread
def start_humidity_actuator_thread():
    thread = threading.Thread(target=run_actuator_control, daemon=True)
    thread.start()
