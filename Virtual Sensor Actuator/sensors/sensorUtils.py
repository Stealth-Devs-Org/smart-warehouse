

sensor_state = {"sensor_type": "", "sensor_id": "","partition_ID": 0, "sensor_location": "", "reading": 0.0, "current_status": 0}

def SetSensorState(type, id,partID, location, reading, status):
    global sensor_state
    sensor_state["sensor_type"] = type
    sensor_state["sensor_id"] = id
    sensor_state["partition_id"] = partID
    sensor_state["sensor_location"] = location
    sensor_state["reading"] = reading
    sensor_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)
    #print(f"Received new sensor state: {sensor_state}")


