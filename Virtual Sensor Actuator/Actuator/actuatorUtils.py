import os
import json

actuator_state = {"actuator_type": "", "actuator_id": "","partition_id": 0, "actuator_location": "", "rate_of_Change": 0.0, "current_status": 0}


# desired_warehouse_temperature_values = [25.0, 25.5, 30.0, 25.5, 23.5, 23.8, 38.1]

# desired_warehouse_airquality_values = [500.0, 520.0, 400.0, 700.0, 650.0, 580.0, 600.0] # in ppm

# desired_warehouse_smoke_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3] # binary value?

# desired_warehouse_humidity_values = [45.0, 47.5, 48.0, 49.5, 44.0, 50.2, 46.8]  # in %RH


def SetActuatorState(type, id,partID, location, reading, status):
    global actuator_state
    actuator_state["actuator_type"] = type
    actuator_state["actuator_id"] = id
    actuator_state["partition_id"] = partID
    actuator_state["actuator_location"] = location
    actuator_state["rate_of_Change"] = reading
    actuator_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)
    #print(f"Received new actuator state: {actuator_state}")


