

actuator_state = {"actuator_type": "", "actuator_id": "","partition_ID": 0, "actuator_location": "", "reading": 0.0, "current_status": 0}

def SetActuatorState(type, id,partID, location, reading, status):
    global actuator_state
    actuator_state["actuator_type"] = type
    actuator_state["actuator_id"] = id
    actuator_state["partition_id"] = partID
    actuator_state["actuator_location"] = location
    actuator_state["reading"] = reading
    actuator_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)
    #print(f"Received new actuator state: {actuator_state}")


