import threading
import time
import paho.mqtt.client as mqtt
import json
import random

from actuatorUtils import SetActuatorState, actuator_state, desired_warehouse_humidity_values  # Import the desired values

HumidityControllerID = [
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
TOPIC = "/actuator_HumidityController" # MQTT topic for the humidity controller actuator

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

def update_json_data(humidity_value, partitionID):
    filepath = 'Virtual Sensor Actuator/warehouse_Env_data.json'  
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        data["Humidity Values"][partitionID] = humidity_value  # Update humidity values

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        print(f"Error: {filepath} not found!")
    except json.JSONDecodeError:
        print(f"Error: JSON file {filepath} is not properly formatted!")


class HumidityController(threading.Thread):
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
            self.adjust_values(rate_of_change, "Humidity Values")
            SetActuatorState("HumidityController", self.actuator_id, self.partition_id, self.actuator_id, round(rate_of_change, 2), 1)
            print(f"Actuator state: {actuator_state}")
            self.client.publish(TOPIC, str(actuator_state))
            time.sleep(random.uniform(1, 4))

    def stop(self):
        self.running = False
        self.client.loop_stop()

    def get_rate_of_change(self):
        return 1  # Example rate of change for the humidity

    def adjust_values(self, rate_of_change, variable):
        sensor_data = load_json_data()
        current_humidity_values = sensor_data.get("Humidity Values", []) # Get the current humidity values from the JSON file

        desired_humidity_values = desired_warehouse_humidity_values  # Using imported values from actuatorUtils

        if len(current_humidity_values) == 0 or len(desired_humidity_values) == 0:
            print(f"Error: Missing humidity data.")
            return

        current_humidity = current_humidity_values[self.partition_id] # Get the current humidity for the partition
        desired_humidity = desired_humidity_values[self.partition_id] # Get the desired humidity for the partition

        # Adjust humidity based on the desired humidity and rate of change
        if abs(desired_humidity - current_humidity) < rate_of_change:
            current_humidity = desired_humidity
        elif desired_humidity > current_humidity:
            current_humidity += rate_of_change
        elif desired_humidity < current_humidity:
            current_humidity -= rate_of_change

        # Update the humidity values in the JSON file
        # current_humidity_values[self.partition_id] = round(current_humidity, 1)

        # Write the updated values back to the JSON file
        update_json_data(current_humidity, self.partition_id)

# Main function to initialize actuators
def main():
    no_of_partitions = len(HumidityControllerID)
    allActuators = []

    for j in range(no_of_partitions):
        allActuators.append([])  # Initialize the actuator list for each partition
        for coord in HumidityControllerID[j]:
            actuator = HumidityController(actuator_id=coord, partition_id=j)
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
