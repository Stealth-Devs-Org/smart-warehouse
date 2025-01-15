
import os

sensor_state = {"sensor_type": "", "sensor_id": "","partition_id": 0, "sensor_location": "", "reading": 0.0, "current_status": 1}

def SetSensorState(type, id,partID, location, reading, status):
    global sensor_state
    sensor_state["sensor_type"] = type
    sensor_state["sensor_id"] = id
    sensor_state["partition_id"] = partID
    sensor_state["sensor_location"] = location
    sensor_state["reading"] = reading
    sensor_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)
    #print(f"Received new sensor state: {sensor_state}")



directory = 'Virtual Sensor Actuator'
filename = 'warehouse_Env_data.txt'
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
    file_path = 'warehouse_Env_data.json'
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

