# import threading
# import os
# import time
# import sys
# import paho.mqtt.client as mqtt
# from actuatorUtils import SetActuatorState, actuator_state, ReadVariableFromDatabase, desired_warehouse_temperature_values
# # sys.path.append('Virtual Sensor Actuator')





# AirConditionerID = [
#     # Partition 0
#     ["(2,2)"],
    
#     # Partition 1
#     ["(9,11)"],
    
#     # Partition 2
#     ["(28,11)"],
    
#     # Partition 3
#     ["(5,15)"],
    
#     # Partition 4
#     ["(12,27)"],
    
#     # Partition 5
#     ["(52,13)"],
    
#     # Partition 6
#     ["(28,18)"]
# ]

# BROKER = "localhost"  
# PORT = 1883
# TOPIC = "/actuator_AirConditioner"

# class AirConditioner(threading.Thread):
#     def __init__(self, actuator_id, partition_id):
#         threading.Thread.__init__(self)
#         self.client = mqtt.Client()
#         self.actuator_id = actuator_id
#         self.partition_id = partition_id
#         self.running = True  

#     def connect_mqtt(self):
#         self.client.connect(BROKER, PORT, 60)
#         self.client.loop_start()  #loop in seperate thread...
        
#     def run(self):
#         self.connect_mqtt()
#         while self.running:
#             rateofChange = self.get_RateofChange()
#             self.AdjustValues(rateofChange, "Temperature Values")
#             SetActuatorState("AirConditioner", self.actuator_id,  self.partition_id,self.actuator_id, round(rateofChange, 2), 1)
#             print(f"Actuator state: {actuator_state}")
#             self.client.publish(TOPIC, str(actuator_state)) 
#             time.sleep(1.2)

#     def stop(self):
#         self.running = False
#         self.client.loop_stop()

#     # def get_temperature_value(self):
#     #     global warehouse_temperature_values
#     #     base_temperature = warehouse_temperature_values[self.partition_id]
#     #     variation = random.uniform(-0.1, 0.1)
#     #     return base_temperature + variation



#     def get_RateofChange(self):  # optional to send in Mqtt
#         rateofchange = 0.3
#         return rateofchange

#     def AdjustValues(self,rateOfChange, varaible):
#         warehouse_temperature_values = ReadVariableFromDatabase("Temperature Values")
#         global desired_warehouse_temperature_values


#         if desired_warehouse_temperature_values[self.partition_id] - warehouse_temperature_values[self.partition_id] < rateOfChange and desired_warehouse_temperature_values[self.partition_id] - warehouse_temperature_values[self.partition_id] > 0:
#             warehouse_temperature_values[self.partition_id] = desired_warehouse_temperature_values[self.partition_id]
#             self.writeValuesToDatabase(warehouse_temperature_values, varaible)

#         elif desired_warehouse_temperature_values[self.partition_id] > warehouse_temperature_values[self.partition_id]:
#             value = warehouse_temperature_values[self.partition_id] + rateOfChange
#             warehouse_temperature_values[self.partition_id] = round(value, 1)

#             self.writeValuesToDatabase(warehouse_temperature_values, varaible)
        
#         elif desired_warehouse_temperature_values[self.partition_id] < warehouse_temperature_values[self.partition_id]:
#             value = warehouse_temperature_values[self.partition_id] - rateOfChange
#             warehouse_temperature_values[self.partition_id] = round(value, 1)
#             self.writeValuesToDatabase(warehouse_temperature_values ,varaible)

    

#     def writeValuesToDatabase(self, values, variable):
#         directory = 'Virtual Sensor Actuator'
#         filename = 'warehouse_Env_data.txt'
#         filepath = os.path.join(directory, filename)

#         # Read existing data from the file
#         if os.path.exists(filepath):
#             with open(filepath, 'r') as file:
#                 lines = file.readlines()
#         else:
#             lines = [
#                 "Temperature Values :\n\n",
#                 "AirQuality Values :\n\n",
#                 "Smoke Values :\n\n",
#                 "Humidity Values :\n\n"
#             ]

#         # Update the specific variable's data
#         if variable == "Temperature Values":
#             index = lines.index("Temperature Values :\n") + 1
#             lines[index] = ', '.join(map(str, values)) + "\n\n"
#         elif variable == "AirQuality Values":
#             index = lines.index("AirQuality Values :\n") + 1
#             lines[index] = ', '.join(map(str, values)) + "\n\n"
#         elif variable == "Smoke Values":
#             index = lines.index("Smoke Values :\n") + 1
#             lines[index] = ', '.join(map(str, values)) + "\n\n"
#         elif variable == "Humidity Values":
#             index = lines.index("Humidity Values :\n") + 1
#             lines[index] = ', '.join(map(str, values)) + "\n\n"

#         # Write updated data back to the file
#         with open(filepath, 'w') as file:
#             file.writelines(lines)



            


# def main():
#     no_of_partitions = len(AirConditionerID)
#     allActuators = []

#     for j in range(no_of_partitions):
#         allActuators.append([])
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
        

# if __name__ == "__main__":
#     main()












# import threading
# import os
# import time
# import paho.mqtt.client as mqtt
# import json
# import sys

# from actuatorUtils import SetActuatorState, actuator_state


# # sys.path.append('Virtual Sensor Actuator\warehouse_Env_data.json')




# AirConditionerID = [
#     # Partition 0
#     ["(2,2)"],

#     # Partition 1
#     ["(9,11)"],

#     # Partition 2
#     ["(28,11)"],

#     # Partition 3
#     ["(5,15)"],

#     # Partition 4
#     ["(12,27)"],

#     # Partition 5
#     ["(52,13)"],

#     # Partition 6
#     ["(28,18)"]
# ]

# BROKER = "localhost"
# PORT = 1883
# TOPIC = "/actuator_AirConditioner"

# # Load the JSON file containing current and desired temperature values
# def load_json_data():
#     filepath = 'warehouse_Env_data.json'  # Path to your JSON file
#     if os.path.exists(filepath):
#         with open(filepath, 'r') as f:
#             return json.load(f)
#     else:
#         print(f"Error: {filepath} not found!")
#         return {}

# # Update the JSON file with the adjusted temperature values
# def update_json_data(temp_values):
#     filepath = 'sensor_data.json'  # Path to your JSON file
#     with open(filepath, 'r') as f:
#         data = json.load(f)

#     data["Temperature Values"] = temp_values  # Update temperature values
#     with open(filepath, 'w') as f:
#         json.dump(data, f, indent=4)

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
#             rate_of_change = self.get_RateofChange()
#             self.AdjustValues(rate_of_change, "Temperature Values")
#             SetActuatorState("AirConditioner", self.actuator_id, self.partition_id, self.actuator_id, round(rate_of_change, 2), 1)
#             print(f"Actuator state: {actuator_state}")
#             self.client.publish(TOPIC, str(actuator_state))
#             time.sleep(1.2)

#     def stop(self):
#         self.running = False
#         self.client.loop_stop()

#     def get_RateofChange(self):
#         return 0.3

#     def AdjustValues(self, rate_of_change, variable):
#         # Load data from the JSON file
#         sensor_data = load_json_data()
#         current_temp_values = sensor_data.get("Temperature Values", [])
#         desired_temp_values = sensor_data.get("Desired Temperature Values", [])

#         if len(current_temp_values) == 0 or len(desired_temp_values) == 0:
#             print(f"Error: Missing temperature data in JSON.")
#             return

#         current_temp = current_temp_values[self.partition_id]
#         desired_temp = desired_temp_values[self.partition_id]

#         # Adjust temperature based on the desired temperature and rate of change
#         if desired_temp - current_temp < rate_of_change and desired_temp - current_temp > 0:
#             current_temp = desired_temp
#         elif desired_temp > current_temp:
#             current_temp += rate_of_change
#         elif desired_temp < current_temp:
#             current_temp -= rate_of_change

#         # Update the temperature values in the JSON file
#         current_temp_values[self.partition_id] = round(current_temp, 1)

#         # Write the updated values back to the JSON file
#         update_json_data(current_temp_values)

# def main():
#     no_of_partitions = len(AirConditionerID)
#     allActuators = []

#     for j in range(no_of_partitions):
#         allActuators.append([])
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

# if __name__ == "__main__":
#     main()

























# import threading
# import os
# import time
# import paho.mqtt.client as mqtt
# import json

# from actuatorUtils import SetActuatorState, actuator_state, desired_warehouse_airquality_values

# # Air conditioner IDs for each partition
# AirConditionerID = [
#     ["(2,2)"],  # Partition 0
#     ["(9,11)"],  # Partition 1
#     ["(28,11)"],  # Partition 2
#     ["(5,15)"],  # Partition 3
#     ["(12,27)"],  # Partition 4
#     ["(52,13)"],  # Partition 5
#     ["(28,18)"]   # Partition 6
# ]

# # MQTT Configuration
# BROKER = "localhost"
# PORT = 1883
# TOPIC = "/actuator_AirConditioner"

# # Load JSON data from a file
# def load_json_data():
#     filepath = 'Virtual Sensor Actuator/warehouse_Env_data.json'  # Path to the JSON file
#     try:
#         with open(filepath, 'r') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"Error: {filepath} not found!")
#         return {}
#     except json.JSONDecodeError:
#         print(f"Error: JSON file {filepath} is not properly formatted!")
#         return {}

# # Update JSON data in the file
# def update_json_data(temp_values):
#     filepath = 'Virtual Sensor Actuator/warehouse_Env_data.json'  # Path to the JSON file
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

# # AirConditioner class for managing each partition
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
#             time.sleep(1.2)

#     def stop(self):
#         self.running = False
#         self.client.loop_stop()

#     def get_rate_of_change(self):
#         return 0.3  # Example rate of change for the temperature

#     def adjust_values(self, rate_of_change, variable):
#         # Load data from the JSON file
#         sensor_data = load_json_data()
#         current_temp_values = sensor_data.get("Temperature Values", [])
#         desired_temp_values = sensor_data.get("Desired Temperature Values", [])

#         if len(current_temp_values) == 0 or len(desired_temp_values) == 0:
#             print(f"Error: Missing temperature data in JSON.")
#             return

#         current_temp = current_temp_values[self.partition_id]
#         desired_temp = desired_temp_values[self.partition_id]

#         # Adjust temperature based on the desired temperature and rate of change
#         if desired_temp - current_temp < rate_of_change and desired_temp - current_temp > 0:
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
#         allActuators.append([])
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

def update_json_data(temp_values):
    filepath = 'Virtual Sensor Actuator/warehouse_Env_data.json'  
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        data["Temperature Values"] = temp_values  # Update temperature values

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
            time.sleep(1.2)

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
        current_temp_values[self.partition_id] = round(current_temp, 1)

        # Write the updated values back to the JSON file
        update_json_data(current_temp_values)

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
            time.sleep(1)
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
