import json
import paho.mqtt.client as mqtt
import time
import threading

BROKER = "localhost"
PORT = 1883
TOPIC = "/actuator_control_temperature"

desired_warehouse_temperature_values = [25.0, 25.5, 30.0, 25.5, 23.5, 23.8, 38.1]
threshold = 0.5  # Threshold for "off" condition
filename = 'all_Sensor_Temperature_data.json'

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


def determine_actuator_command(current_temp, desired_temp):
    if abs(desired_temp - current_temp) < threshold:
        return "off"
    elif desired_temp > current_temp:
        return "raise"
    elif desired_temp < current_temp:
        return "reduce"
        return "reduce"
    else:
        return "off"

def send_to_mqtt(commands):
    t1 = time.time()
    commands["t1"] = t1
    commands["t2"] = t1
    commands["t3"] = t1 
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
            for i, avg_temp in partition_averages.items():
                part_index = int(i.replace('part', ''))
                desired_temp = desired_warehouse_temperature_values[part_index]
                actuator_command = determine_actuator_command(avg_temp, desired_temp)
                actuator_commands[f"{i}_actuator"] = actuator_command
            
            send_to_mqtt(actuator_commands)
        
        time.sleep(1)  # 1-second interval

# Start the actuator control in a separate thread
def start_temp_actuator_thread():
    thread = threading.Thread(target=run_actuator_control, daemon=True)
    thread.start()


