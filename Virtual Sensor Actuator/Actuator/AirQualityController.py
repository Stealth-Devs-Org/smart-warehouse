import threading
import time
import paho.mqtt.client as mqtt
import json
import random

from actuatorUtils import SetActuatorState, actuator_state  # Import the desired values

AirQualityControllerID = [
    [],# ["(2,2)"],  # Partition 0
    ["(9,11)"],  # Partition 1
    # ["(28,11)"],  # Partition 2
    # ["(5,15)"],  # Partition 3
    # ["(12,27)"],  # Partition 4
    # ["(52,13)"],  # Partition 5
    # ["(28,18)"]   # Partition 6
]

BROKER = "localhost"
PORT = 1883
TOPICtoPublish = "/actuator_AirQualityController"  # MQTT topic for the air quality controller actuator
TOPICtoSubscribe = "/actuator_control_air_quality"  # Topic for air quality control

# Function to load JSON data
def load_json_data():
    filepath = '../warehouse_Env_data.json'
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found!")
        return {}
    except json.JSONDecodeError:
        print(f"Error: JSON file {filepath} is not properly formatted!")
        return {}

# Function to update JSON data
def update_json_data(air_quality_value, partitionID):
    filepath = '../warehouse_Env_data.json'
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

# Actuator Class
class AirQualityController(threading.Thread):
    def __init__(self, actuator_id, partition_id):
        threading.Thread.__init__(self)
        self.client = mqtt.Client()
        self.actuator_id = actuator_id
        self.partition_id = partition_id
        self.action = ""
        self.running = True

    def connect_mqtt(self):
        # Connect to the broker and subscribe to the control topic
        self.client.connect(BROKER, PORT, 60)
        self.client.subscribe(TOPICtoSubscribe)  # Subscribe to the air quality control topic
        self.client.loop_start()

    def on_message(self, client, userdata, msg):
        """Callback when a message is received on a subscribed topic"""
        data_received = json.loads(msg.payload.decode())
        self.action = data_received.get(f"part{self.partition_id}_actuator", "")

        if self.action == "off":
            self.running = False
            SetActuatorState("AirQualityController", self.actuator_id, self.partition_id, self.actuator_id, 0, 0)
        else:
            self.running = True
            rate_of_change = self.get_rate_of_change()
            SetActuatorState("AirQualityController", self.actuator_id, self.partition_id, self.actuator_id, round(rate_of_change, 2), 1)

        print(f"Actuator state: {actuator_state}")
        self.client.publish(TOPICtoPublish, str(actuator_state))

    def run(self):
        self.connect_mqtt()
        self.client.on_message = self.on_message  # Set the callback for messages
        while self.running:
            self.adjust_values("AirQuality Values")
            time.sleep(random.uniform(1, 4))  # Simulate time passing between actions

    def stop(self):
        self.running = False
        self.client.loop_stop()

    def get_rate_of_change(self):
        return 1  # Example rate of change for the air quality

    def adjust_values(self, variable):
        sensor_data = load_json_data()
        current_air_quality_values = sensor_data.get("AirQuality Values", [])  # Get the current air quality values from the JSON file

        if len(current_air_quality_values) == 0:
            print("Error: Missing air quality data.")
            return

        if self.action == "raise":
            current_air_quality_values[self.partition_id] += 30
        elif self.action == "reduce":
            current_air_quality_values[self.partition_id] -= 30
        elif self.action == "off":
            current_air_quality_values[self.partition_id] += 0

        current_air_quality = current_air_quality_values[self.partition_id]  # Get the current air quality for the partition
        update_json_data(current_air_quality, self.partition_id)


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
