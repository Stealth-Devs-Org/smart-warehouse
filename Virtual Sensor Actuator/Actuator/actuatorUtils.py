import os

actuator_state = {"actuator_type": "", "actuator_id": "","partition_ID": 0, "actuator_location": "", "desired_value": 0.0, "current_status": 0}

def SetActuatorState(type, id,partID, location, reading, status):
    global actuator_state
    actuator_state["actuator_type"] = type
    actuator_state["actuator_id"] = id
    actuator_state["partition_id"] = partID
    actuator_state["actuator_location"] = location
    actuator_state["desired_value"] = reading
    actuator_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)
    #print(f"Received new actuator state: {actuator_state}")



directory = 'Virtual Sensor Actuator'
filename = 'warehouse_Env_data.txt'
filepath = os.path.join(directory, filename)



def ReadVariableFromDatabase(Variable):  # Variable = "Temperature Values", "AirQuality Values", "Smoke Values", "Humidity Values"
    with open(filepath, 'r') as file:
        lines = file.readlines()

    Varaible_values = []
    for i, line in enumerate(lines):
        if Variable in line:
            Variable_values = list(map(float, lines[i + 1].strip().split(', ')))
    
    return Variable_values
    # print("Variable Values:", Variable_values)

