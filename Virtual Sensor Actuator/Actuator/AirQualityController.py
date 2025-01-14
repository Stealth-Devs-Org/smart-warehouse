import threading
import time
import paho.mqtt.client as mqtt
import json
import random

from actuatorUtils import SetActuatorState, actuator_state, desired_warehouse_air_quality_values  # Import the desired values

AirQualityControllerID = [
    ["(2,2)"],  # Partition 0
    ["(9,11)"],  # Partition 1
    ["(28,11)"],  # Partition 2
    ["(5,15)"],  # Partition 3
    ["(12,27)"],  # Partition 4
    ["(52,13)"],  # Partition 5
    ["(28,18)"]   # Partition 6
]


BROKER = "localhost"
PORT = 1883
TOPIC = "/actuator_AirQualityController" # MQTT topic for the air quality controller actuator

def load_json_data():
    filepath = 'Virtual Sensor Actuator/warehouse_Env_data.json'  
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found!")
        return {}
    except json.JSONDecodeError:
        print(f"Error: JSON file {filepath} is not properly formatted!")
        return {}

def update_json_data(air_quality_value, partitionID):
    filepath = 'Virtual Sensor Actuator/warehouse_Env_data.json'  
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        data["AirQuality Values"][partitionID] = air_quality_value  # Update air quality values

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        print(f"Error: {filepath} not found!")
    except json.JSONDecodeError:
        print(f"Error: JSON file {filepath} is not properly formatted!")


class AirQualityController(threading.Thread):
    def __init__(self, actuator_id, partition_id):
        threading.Thread.__init__(self)
        self.client = mqtt.Client()
        self.actuator_id = actuator_id
        self.partition_id = partition_id
        self.running = True

    def connect_mqtt(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()

    def run(self):
        self.connect_mqtt()
        while self.running:
            rate_of_change = self.get_rate_of_change()
            self.adjust_values(rate_of_change, "AirQuality Values")
            SetActuatorState("AirQualityController", self.actuator_id, self.partition_id, self.actuator_id, round(rate_of_change, 2), 1)
            print(f"Actuator state: {actuator_state}")
            self.client.publish(TOPIC, str(actuator_state))
            time.sleep(random.uniform(1, 4))

    def stop(self):
        self.running = False
        self.client.loop_stop()

    def get_rate_of_change(self):
        return 1  # Example rate of change for the air quality

    def adjust_values(self, rate_of_change, variable):
        sensor_data = load_json_data()
        current_air_quality_values = sensor_data.get("AirQuality Values", []) # Get the current air quality values from the JSON file

        desired_air_quality_values = desired_warehouse_air_quality_values  # Using imported values from actuatorUtils

        if len(current_air_quality_values) == 0 or len(desired_air_quality_values) == 0:
            print(f"Error: Missing air quality data.")
            return

        current_air_quality = current_air_quality_values[self.partition_id] # Get the current air quality for the partition
        desired_air_quality = desired_air_quality_values[self.partition_id] # Get the desired air quality for the partition

        # Adjust air quality based on the desired air quality and rate of change
        if abs(desired_air_quality - current_air_quality) < rate_of_change:
            current_air_quality = desired_air_quality
        elif desired_air_quality > current_air_quality:
            current_air_quality += rate_of_change
        elif desired_air_quality < current_air_quality:
            current_air_quality -= rate_of_change

        # Update the air quality values in the JSON file
        # current_air_quality_values[self.partition_id] = round(current_air_quality, 1)

        # Write the updated values back to the JSON file
        update_json_data(current_air_quality, self.partition_id)

# Main function to initialize actuators
def main():
    no_of_partitions = len(AirQualityControllerID)
    allActuators = []

    for j in range(no_of_partitions):
        allActuators.append([])  # Initialize the actuator list for each partition
        for coord in AirQualityControllerID[j]:
            actuator = AirQualityController(actuator_id=coord, partition_id=j)
            allActuators[j].append(actuator)
            actuator.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping all actuators...")
        for partition in allActuators:
            for actuator in partition:
                actuator.stop()
        for partition in allActuators:
            for actuator in partition:
                actuator.join()
        print("All actuators stopped.")

# Entry point for the script
if __name__ == "__main__":
    main()
