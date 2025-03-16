
import os
import csv

sensor_state = {"sensor_type": "", "sensor_id": "","partition_id": 0, "sensor_location": "", "reading": 0.0, "current_status": 1, "t1": 0.0, "t2": 0.0, "t3": 0.0, "t4": 0.0} 

def SetSensorState(type, id,partID, location, reading, status, t1):
    global sensor_state
    sensor_state["sensor_type"] = type
    sensor_state["sensor_id"] = id
    sensor_state["partition_id"] = partID
    sensor_state["sensor_location"] = location
    sensor_state["reading"] = reading
    sensor_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)
    sensor_state["t1"] = t1
    sensor_state["t2"] = t1
    sensor_state["t3"] = t1
    sensor_state["t4"] = t1
    #print(f"Received new sensor state: {sensor_state}")



directory = 'Virtual Sensor Actuator'
filename = '../warehouse_Env_data.txt'
filepath = os.path.join(directory, filename)


# def ReadVariableFromDatabase(Variable):  # Variable = "Temperature Values", "AirQuality Values", "Smoke Values", "Humidity Values"
#     with open(filepath, 'r') as file:
#         lines = file.readlines()

#     Varaible_values = []
#     for i, line in enumerate(lines):
#         if Variable in line:
#             Variable_values = list(map(float, lines[i + 1].strip().split(', ')))
    
#     return Variable_values
#     # print("Variable Values:", Variable_values)


import json

def ReadVariableFromDatabase(variable_name):
    # Load the data from the JSON file
    file_path = '../warehouse_Env_data.json'
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Return the corresponding variable (in this case, Temperature Values)
        if variable_name == "Temperature Values":
            return data.get("Temperature Values", [])
        
        elif variable_name == "AirQuality Values":
            return data.get("AirQuality Values", [])
            
        elif variable_name == "Humidity Values":
            return data.get("Humidity Values", [])
        else:
            return []
        
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []


def SaveToCSV(data, t4, filename):
    # Check if file exists
    file_exists = os.path.isfile(filename)

    # Open CSV file in append mode
    with open(filename, mode="a", newline='') as file:
        writer = csv.writer(file)

        # If file does not exist, write the header
        if not file_exists:
            writer.writerow(["Sensor_Id", "Partition_ID", "Sensor_Type", "t1", "t2", "t3", "t4"])  # Write the header
        sensor_id = data.get("sensor_id", "unknown")
        partition_id = data.get("partition_id", -1)
        sensor_type = data.get("sensor_type", "unknown")
        t1 = data.get("t1", 0.0)
        t2 = data.get("t2", 0.0)
        t3 = data.get("t3", 0.0)
        # Write the row with timestamps
        writer.writerow([sensor_id, partition_id, sensor_type, t1, t2, t3, t4])
