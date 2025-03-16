import threading
import time
import paho.mqtt.client as mqtt
import json
import random

from actuatorUtils import SetActuatorState, actuator_state  # Import the desired values

AirConditionerID = [
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
TOPICtoPublish = "/actuator_AirConditioner"  # MQTT topic for the air conditioner actuator
TOPICtoSubscribe = "/actuator_control_temperature"  # Topic for temperature control


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
def update_json_data(temp_value, partitionID):
    filepath = '../warehouse_Env_data.json'
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        data["Temperature Values"][partitionID] = temp_value  # Update temperature values

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        print(f"Error: {filepath} not found!")
    except json.JSONDecodeError:
        print(f"Error: JSON file {filepath} is not properly formatted!")


# # Function to load the data from the actuator control topic
# def update_json_from_actuator_control():
#     return load_json_data()


# Actuator Class
class AirConditioner(threading.Thread):
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
        self.client.subscribe(TOPICtoSubscribe)  # Subscribe to the temperature control topic
        self.client.loop_start()

    def on_message(self, client, userdata, msg):
        """Callback when a message is received on a subscribed topic"""
        data_received = json.loads(msg.payload.decode())
        self.action = data_received.get(f"part{self.partition_id}_actuator", "")
        #print(f"Action received for partition {self.partition_id}: {action}")
        
        if self.action == "off":
            self.running = False
            SetActuatorState("AirConditioner", self.actuator_id, self.partition_id, self.actuator_id, 0, 0)

        else:
            self.running = True
            rate_of_change = self.get_rate_of_change()
            SetActuatorState("AirConditioner", self.actuator_id, self.partition_id, self.actuator_id, round(rate_of_change, 2), 1)

        print(f"Actuator state: {actuator_state}")
        self.client.publish(TOPICtoPublish, str(actuator_state))

    def run(self):
        self.connect_mqtt()
        self.client.on_message = self.on_message  # Set the callback for messages
        while self.running:
            self.adjust_values("Temperature Values")
            time.sleep(random.uniform(1, 4))  # Simulate time passing between actions

    def stop(self):
        self.running = False
        self.client.loop_stop()

    def get_rate_of_change(self):
        return 1  # Example rate of change for the temperature

    def adjust_values(self, variable):
        sensor_data = load_json_data()
        current_temp_values = sensor_data.get("Temperature Values", [])  # Get the current temperature values from the JSON file

        if len(current_temp_values) == 0:
            print("Error: Missing temperature data.")
            return

        # data_received = json.loads(msg.payload.decode())

        # action = data_received.get(f"part{self.partition_id}_actuator", "")
        # print(f"Action received for partition {self.partition_id}: {action}")
        if self.action == "raise":
            current_temp_values[self.partition_id] += 1
        elif self.action == "reduce":
            current_temp_values[self.partition_id] -= 1
        
        elif self.action == "off":
            current_temp_values[self.partition_id] +=0

        current_temp = current_temp_values[self.partition_id]  # Get the current temperature for the partition
        

        # Here, we would adjust the values (this can be expanded based on the received actions)
        update_json_data(current_temp, self.partition_id)
        


# Main function to initialize actuators
def main():
    no_of_partitions = len(AirConditionerID)
    allActuators = []

    for j in range(no_of_partitions):
        allActuators.append([])  # Initialize the actuator list for each partition
        for coord in AirConditionerID[j]:
            actuator = AirConditioner(actuator_id=coord, partition_id=j)
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
