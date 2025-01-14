# import threading
# import time
# import paho.mqtt.client as mqtt
# import json


# from actuatorUtils import SetActuatorState, actuator_state, desired_warehouse_temperature_values  # Import the desired values


# AirConditionerID = [
#     ["(2,2)"],  # Partition 0
#     ["(9,11)"],  # Partition 1
#     ["(28,11)"],  # Partition 2
#     ["(5,15)"],  # Partition 3
#     ["(12,27)"],  # Partition 4
#     ["(52,13)"],  # Partition 5
#     ["(28,18)"]   # Partition 6
# ]


# BROKER = "localhost"
# PORT = 1883
# TOPIC = "/actuator_AirConditioner" # MQTT topic for the air conditioner actuator

# def load_json_data():
#     filepath = 'Virtual Sensor Actuator/warehouse_Env_data.json'  
#     try:
#         with open(filepath, 'r') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"Error: {filepath} not found!")
#         return {}
#     except json.JSONDecodeError:
#         print(f"Error: JSON file {filepath} is not properly formatted!")
#         return {}

# def update_json_data(temp_values):
#     filepath = 'Virtual Sensor Actuator/warehouse_Env_data.json'  
#     try:
#         with open(filepath, 'r') as f:
#             data = json.load(f)

#         data["Temperature Values"] = temp_values  # Update temperature values

#         with open(filepath, 'w') as f:
#             json.dump(data, f, indent=4)
#     except FileNotFoundError:
#         print(f"Error: {filepath} not found!")
#     except json.JSONDecodeError:
#         print(f"Error: JSON file {filepath} is not properly formatted!")


# class AirConditioner(threading.Thread):
#     def __init__(self, actuator_id, partition_id):
#         threading.Thread.__init__(self)
#         self.client = mqtt.Client()
#         self.actuator_id = actuator_id
#         self.partition_id = partition_id
#         self.running = True

#     def connect_mqtt(self):
#         self.client.connect(BROKER, PORT, 60)
#         self.client.loop_start()

#     def run(self):
#         self.connect_mqtt()
#         while self.running:
#             rate_of_change = self.get_rate_of_change()
#             self.adjust_values(rate_of_change, "Temperature Values")
#             SetActuatorState("AirConditioner", self.actuator_id, self.partition_id, self.actuator_id, round(rate_of_change, 2), 1)
#             print(f"Actuator state: {actuator_state}")
#             self.client.publish(TOPIC, str(actuator_state))
#             time.sleep(5)

#     def stop(self):
#         self.running = False
#         self.client.loop_stop()

#     def get_rate_of_change(self):
#         return 1  # Example rate of change for the temperature

#     def adjust_values(self, rate_of_change, variable):
#         sensor_data = load_json_data()
#         current_temp_values = sensor_data.get("Temperature Values", []) # Get the current temperature values from the JSON file

#         desired_temp_values = desired_warehouse_temperature_values  # Using imported values from actuatorUtils

#         if len(current_temp_values) == 0 or len(desired_temp_values) == 0:
#             print(f"Error: Missing temperature data.")
#             return

#         current_temp = current_temp_values[self.partition_id] # Get the current temperature for the partition
#         desired_temp = desired_temp_values[self.partition_id] # Get the desired temperature for the partition

#         # Adjust temperature based on the desired temperature and rate of change
#         if abs(desired_temp - current_temp) < rate_of_change:
#             current_temp = desired_temp
#         elif desired_temp > current_temp:
#             current_temp += rate_of_change
#         elif desired_temp < current_temp:
#             current_temp -= rate_of_change

#         # Update the temperature values in the JSON file
#         current_temp_values[self.partition_id] = round(current_temp, 1)

#         # Write the updated values back to the JSON file
#         update_json_data(current_temp_values)

# # Main function to initialize actuators
# def main():
#     no_of_partitions = len(AirConditionerID)
#     allActuators = []

#     for j in range(no_of_partitions):
#         allActuators.append([])  # Initialize the actuator list for each partition
#         for coord in AirConditionerID[j]:
#             actuator = AirConditioner(actuator_id=coord, partition_id=j)
#             allActuators[j].append(actuator)
#             actuator.start()

#     try:
#         while True:
#             time.sleep(1)
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


from actuatorUtils import SetActuatorState, actuator_state, desired_warehouse_temperature_values  # Import the desired values


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
TOPIC = "/actuator_AirConditioner" # MQTT topic for the air conditioner actuator

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

def update_json_data(temp_value, partitionID):
    filepath = 'Virtual Sensor Actuator/warehouse_Env_data.json'  
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


class AirConditioner(threading.Thread):
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
            self.adjust_values(rate_of_change, "Temperature Values")
            SetActuatorState("AirConditioner", self.actuator_id, self.partition_id, self.actuator_id, round(rate_of_change, 2), 1)
            print(f"Actuator state: {actuator_state}")
            self.client.publish(TOPIC, str(actuator_state))
            time.sleep(random.uniform(1, 4))

    def stop(self):
        self.running = False
        self.client.loop_stop()

    def get_rate_of_change(self):
        return 1  # Example rate of change for the temperature

    def adjust_values(self, rate_of_change, variable):
        sensor_data = load_json_data()
        current_temp_values = sensor_data.get("Temperature Values", []) # Get the current temperature values from the JSON file

        desired_temp_values = desired_warehouse_temperature_values  # Using imported values from actuatorUtils

        if len(current_temp_values) == 0 or len(desired_temp_values) == 0:
            print(f"Error: Missing temperature data.")
            return

        current_temp = current_temp_values[self.partition_id] # Get the current temperature for the partition
        desired_temp = desired_temp_values[self.partition_id] # Get the desired temperature for the partition

        # Adjust temperature based on the desired temperature and rate of change
        if abs(desired_temp - current_temp) < rate_of_change:
            current_temp = desired_temp
        elif desired_temp > current_temp:
            current_temp += rate_of_change
        elif desired_temp < current_temp:
            current_temp -= rate_of_change

        # Update the temperature values in the JSON file
        # current_temp_values[self.partition_id] = round(current_temp, 1)

        # Write the updated values back to the JSON file
        update_json_data(current_temp,self.partition_id)

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
