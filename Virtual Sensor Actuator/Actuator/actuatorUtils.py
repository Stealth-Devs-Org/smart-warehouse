import os
import json

actuator_state = {"actuator_type": "", "actuator_id": "","partition_id": 0, "actuator_location": "", "rate_of_Change": 0.0, "current_status": 0}


desired_warehouse_temperature_values = [25.0, 25.5, 30.0, 25.5, 23.5, 23.8, 38.1]

desired_warehouse_airquality_values = [500.0, 520.0, 400.0, 700.0, 650.0, 580.0, 600.0] # in ppm

desired_warehouse_smoke_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3] # binary value?

desired_warehouse_humidity_values = [45.0, 47.5, 48.0, 49.5, 44.0, 50.2, 46.8]  # in %RH


def SetActuatorState(type, id,partID, location, reading, status):
    global actuator_state
    actuator_state["actuator_type"] = type
    actuator_state["actuator_id"] = id
    actuator_state["partition_id"] = partID
    actuator_state["actuator_location"] = location
    actuator_state["rate_of_Change"] = reading
    actuator_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)
    #print(f"Received new actuator state: {actuator_state}")



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


# def ReadVariableFromDatabase(Variable):
#     if not os.path.exists(filepath):
#         print(f"Error: File {filepath} does not exist.")
#         return []

#     with open(filepath, 'r') as file:
#         lines = file.readlines()

#     Variable_values = []
#     for i, line in enumerate(lines):
#         if Variable in line:
#             try:
#                 Variable_values = list(map(float, lines[i + 1].strip().split(', ')))
#             except ValueError:
#                 print(f"Error: Unable to parse values for {Variable} in the file.")
#             break
    
#     if not Variable_values:
#         print(f"Warning: {Variable} not found in the file or no valid values present.")
    
#     return Variable_values








# def ReadVariableFromDatabase(variable_name, update_value=None):
#     """
#     Reads or updates a specific variable in a JSON file.

#     :param variable_name: The name of the variable to read or update.
#     :param update_value: If provided, updates the variable with this new value.
#     :return: The value of the variable or an empty list if not found.
#     """
#     file_path = 'Virtual Sensor Actuator/warehouse_Env_data.json'
    
#     # Try to read the data from the JSON file
#     try:
#         with open(file_path, 'r') as file:
#             data = json.load(file)
        
#         # If update_value is provided, update the variable and write it back to the JSON
#         if update_value is not None:
#             # Update the variable in the data
#             data[variable_name] = update_value
            
#             # Write the updated data back to the file
#             with open(file_path, 'w') as file:
#                 json.dump(data, file, indent=4)
#             print(f"Updated {variable_name} in the database.")
        
#         # Return the corresponding variable's value, or an empty list if it doesn't exist
#         return data.get(variable_name, [])
    
#     except FileNotFoundError:
#         print(f"Error: {file_path} not found.")
#         return []
#     except json.JSONDecodeError:
#         print(f"Error: JSON in {file_path} is not properly formatted.")
#         return []