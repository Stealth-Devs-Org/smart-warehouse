# import threading
# import time
# import paho.mqtt.client as mqtt
# import json
# import random

# from actuatorUtils import SetActuatorState, actuator_state  # Import the desired values

# HumidityControllerID = [
#     ["(2,3)"],  # Partition 0
#     ["(10,12)"],  # Partition 1
#     ["(29,12)"],  # Partition 2
#     ["(6,16)"],  # Partition 3
#     ["(13,28)"],  # Partition 4
#     ["(53,14)"],  # Partition 5
#     ["(29,19)"]   # Partition 6
# ]

# BROKER = "localhost"
# PORT = 1883
# TOPICtoPublish = "/actuator_HumidityController"  # MQTT topic for the humidity controller actuator
# TOPICtoSubscribe = "/actuator_control_humidity"  # Topic for humidity control

# # Function to load JSON data
# def load_json_data():
#     filepath = 'warehouse_Env_data.json'
#     try:
#         with open(filepath, 'r') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"Error: {filepath} not found!")
#         return {}
#     except json.JSONDecodeError:
#         print(f"Error: JSON file {filepath} is not properly formatted!")
#         return {}

# # Function to update JSON data
# def update_json_data(humidity_value, partitionID):
#     filepath = 'warehouse_Env_data.json'
#     try:
#         with open(filepath, 'r') as f:
#             data = json.load(f)

#         data["Humidity Values"][partitionID] = humidity_value  # Update humidity values

#         with open(filepath, 'w') as f:
#             json.dump(data, f, indent=4)
#     except FileNotFoundError:
#         print(f"Error: {filepath} not found!")
#     except json.JSONDecodeError:
#         print(f"Error: JSON file {filepath} is not properly formatted!")

# # Actuator Class
# class HumidityController(threading.Thread):
#     def __init__(self, actuator_id, partition_id):
#         threading.Thread.__init__(self)
#         self.client = mqtt.Client()
#         self.actuator_id = actuator_id
#         self.partition_id = partition_id
#         self.action = ""
#         self.running = True

#     def connect_mqtt(self):
#         # Connect to the broker and subscribe to the control topic
#         self.client.connect(BROKER, PORT, 60)
#         self.client.subscribe(TOPICtoSubscribe)  # Subscribe to the humidity control topic
#         self.client.loop_start()

#     def on_message(self, client, userdata, msg):
#         """Callback when a message is received on a subscribed topic"""
#         data_received = json.loads(msg.payload.decode())
#         self.action = data_received.get(f"part{self.partition_id}_actuator", "")

#         if self.action == "off":
#             self.running = False
#             SetActuatorState("HumidityController", self.actuator_id, self.partition_id, self.actuator_id, 0, 0)
#         else:
#             self.running = True
#             rate_of_change = self.get_rate_of_change()
#             SetActuatorState("HumidityController", self.actuator_id, self.partition_id, self.actuator_id, round(rate_of_change, 2), 1)

#         print(f"Actuator state: {actuator_state}")
#         self.client.publish(TOPICtoPublish, str(actuator_state))

#     def run(self):
#         self.connect_mqtt()
#         self.client.on_message = self.on_message  # Set the callback for messages
#         while self.running:
#             self.adjust_values("Humidity Values")
#             time.sleep(random.uniform(1, 4))  # Simulate time passing between actions

#     def stop(self):
#         self.running = False
#         self.client.loop_stop()

#     def get_rate_of_change(self):
#         return 0.5  # Example rate of change for humidity

#     def adjust_values(self, variable):
#         sensor_data = load_json_data()
#         current_humidity_values = sensor_data.get("Humidity Values", [])  # Get the current humidity values from the JSON file

#         if len(current_humidity_values) == 0:
#             print("Error: Missing humidity data.")
#             return

#         if self.action == "raise":
#             current_humidity_values[self.partition_id] += 1
#         elif self.action == "reduce":
#             current_humidity_values[self.partition_id] -= 1
#         elif self.action == "off":
#             current_humidity_values[self.partition_id] += 0

#         current_humidity = current_humidity_values[self.partition_id]  # Get the current humidity for the partition
#         update_json_data(current_humidity, self.partition_id)

# # Main function to initialize actuators
# def main():
#     no_of_partitions = len(HumidityControllerID)
#     allActuators = []

#     for j in range(no_of_partitions):
#         allActuators.append([])  # Initialize the actuator list for each partition
#         for coord in HumidityControllerID[j]:
#             actuator = HumidityController(actuator_id=coord, partition_id=j)
#             allActuators[j].append(actuator)
#             actuator.start()

#     try:
#         while True:
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("\nStopping all actuators...")
#         for partition in allActuators:
#             for actuator in partition:
#                 actuator.stop()
#         for partition in allActuators:
#             for actuator in partition:
#                 actuator.join()
#         print("All actuators stopped.")

# # Entry point for the script
# if __name__ == "__main__":
#     main()














import threading
import time
import paho.mqtt.client as mqtt
import json
import random

from actuatorUtils import SetActuatorState, actuator_state  # Import the desired values

# Global lock for JSON file access
json_lock = threading.Lock()

HumidityControllerID = [
    ["(2,3)"],    # Partition 0
    ["(10,12)"],  # Partition 1
    ["(29,12)"],  # Partition 2
    ["(6,16)"],   # Partition 3
    ["(13,28)"],  # Partition 4
    ["(53,14)"],  # Partition 5
    ["(29,19)"]   # Partition 6
]

BROKER = "localhost"
PORT = 1883
TOPICtoPublish = "/actuator_HumidityController"  # MQTT topic for the humidity controller actuator
TOPICtoSubscribe = "/actuator_control_humidity"  # Topic for humidity control

# Function to load JSON data
def load_json_data():
    filepath = 'warehouse_Env_data.json'
    try:
        with json_lock:  # Synchronize access to JSON file
            with open(filepath, 'r') as f:
                return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found!")
        return {}
    except json.JSONDecodeError:
        print(f"Error: JSON file {filepath} is not properly formatted!")
        return {}

# Function to update JSON data
def update_json_data(humidity_value, partitionID):
    filepath = 'warehouse_Env_data.json'
    try:
        with json_lock:  # Synchronize access to JSON file
            with open(filepath, 'r') as f:
                data = json.load(f)
            data["Humidity Values"][partitionID] = humidity_value  # Update humidity values
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        #print(f"Updated JSON - Partition {partitionID}: Humidity = {humidity_value}")
    except FileNotFoundError:
        print(f"Error: {filepath} not found!")
    except json.JSONDecodeError:
        print(f"Error: JSON file {filepath} is not properly formatted!")

# Actuator Class
class HumidityController(threading.Thread):
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
        self.client.subscribe(TOPICtoSubscribe)  # Subscribe to the humidity control topic
        print(f"Actuator {self.actuator_id} subscribed to {TOPICtoSubscribe}")
        self.client.loop_start()

    def on_message(self, client, userdata, msg):
        """Callback when a message is received on a subscribed topic"""
        data_received = json.loads(msg.payload.decode())
        self.action = data_received.get(f"part{self.partition_id}_actuator", "")
        print(f"Actuator {self.actuator_id} received action: {self.action}")

        if self.action == "off":
            self.running = False
            SetActuatorState("HumidityController", self.actuator_id, self.partition_id, self.actuator_id, 0, 0)
        else:
            self.running = True
            rate_of_change = self.get_rate_of_change()
            SetActuatorState("HumidityController", self.actuator_id, self.partition_id, self.actuator_id, round(rate_of_change, 2), 1)
            self.adjust_values("Humidity Values")  # Immediately adjust values on receiving command

        print(f"Actuator state: {actuator_state}")
        self.client.publish(TOPICtoPublish, str(actuator_state))

    def run(self):
        self.connect_mqtt()
        self.client.on_message = self.on_message  # Set the callback for messages
        while self.running:
            time.sleep(0.1)  # Keep thread alive without heavy computation

    def stop(self):
        self.running = False
        self.client.loop_stop()

    def get_rate_of_change(self):
        return 0.5  # Example rate of change for humidity

    def adjust_values(self, variable):
        sensor_data = load_json_data()
        current_humidity_values = sensor_data.get("Humidity Values", [])  # Get the current humidity values from the JSON file

        if len(current_humidity_values) == 0:
            print("Error: Missing humidity data.")
            return

        print(f"Partition {self.partition_id} - Action: {self.action}, Current Humidity: {current_humidity_values[self.partition_id]}")
        if self.action == "raise":
            current_humidity_values[self.partition_id] += 1
        elif self.action == "reduce":
            current_humidity_values[self.partition_id] -= 1
        elif self.action == "off":
            current_humidity_values[self.partition_id] += 0  # No change

        current_humidity = current_humidity_values[self.partition_id]  # Get the updated humidity for the partition
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