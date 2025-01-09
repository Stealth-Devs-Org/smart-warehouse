import json
import random
import threading
import time
from server.agv.keep_alive import permanent_obstacles
from server.agv.utils import Update_working_agvs_json
from server.mqtt.utils import mqtt_client

working_agvs = {}

inbound_pallet_locations = {}
outbound_pallet_locations = {}
storage_pallet_locations = {}

# Assigning pallet locations with respective path location
for y in range(5, 12):
    inbound_pallet_locations[(18, y)] = (17, y)
    # inbound_pallet_locations[(19, y)] = (20, y)
    # inbound_pallet_locations[(21, y)] = (20, y)
    # inbound_pallet_locations[(22, y)] = (23, y)
    outbound_pallet_locations[(25, y)] = (24, y)
    # outbound_pallet_locations[(26, y)] = (27, y)
    # outbound_pallet_locations[(28, y)] = (27, y)
    # outbound_pallet_locations[(29, y)] = (30, y)

for x in range(11, 22):
    # storage_pallet_locations[(x, 27)] = (x, 28)
    # storage_pallet_locations[(x, 26)] = (x, 25)
    # storage_pallet_locations[(x, 24)] = (x, 25)
    # storage_pallet_locations[(x, 23)] = (x, 22)
    # storage_pallet_locations[(x, 21)] = (x, 22)
    # storage_pallet_locations[(x, 20)] = (x, 19)
    # storage_pallet_locations[(x, 18)] = (x, 19)
    storage_pallet_locations[(x, 17)] = (x, 16)

# for x in range(25, 36):
#     storage_pallet_locations[(x, 27)] = (x, 28)
#     storage_pallet_locations[(x, 26)] = (x, 25)
#     storage_pallet_locations[(x, 24)] = (x, 25)
#     storage_pallet_locations[(x, 23)] = (x, 22)
#     storage_pallet_locations[(x, 21)] = (x, 22)
#     storage_pallet_locations[(x, 20)] = (x, 19)
#     storage_pallet_locations[(x, 18)] = (x, 19)
#     storage_pallet_locations[(x, 17)] = (x, 16)


def generate_random_task():
    # Randomly selecting a pallet to move
    in_or_out = random.choice(["inbound", "outbound"])
    if in_or_out == "inbound":
        start_locations = list(inbound_pallet_locations.keys())
        end_locations = list(storage_pallet_locations.keys())
        start_pallet_location = random.choice(start_locations)
        start_path_location = inbound_pallet_locations[start_pallet_location]
        end_pallet_location = random.choice(end_locations)
        end_path_location = storage_pallet_locations[end_pallet_location]
    else:
        start_locations = list(storage_pallet_locations.keys())
        end_locations = list(outbound_pallet_locations.keys())
        start_pallet_location = random.choice(start_locations)
        start_path_location = storage_pallet_locations[start_pallet_location]
        end_pallet_location = random.choice(end_locations)
        end_path_location = outbound_pallet_locations[end_pallet_location]

    # Convert tuple to list
    start_pallet_location = list(start_pallet_location)
    start_path_location = list(start_path_location)
    end_pallet_location = list(end_pallet_location)
    end_path_location = list(end_path_location)

    start_pallet_location.append(random.choice([1, 5]))  # Randomly selecting the pallet height
    end_pallet_location.append(random.choice([1, 5]))  # Randomly selecting the pallet height

    task = {
        "halfway": False,
        "assigned_agv": None,
        "start_pallet_location": start_pallet_location,
        "start_path_location": start_path_location,
        "end_pallet_location": end_pallet_location,
        "end_path_location": end_path_location,
    }

    return task


def task_divider(task):
    # Dividing the task into smaller tasks
    start_pallet_location = task["start_pallet_location"]
    start_path_location = task["start_path_location"]
    end_pallet_location = task["end_pallet_location"]
    end_path_location = task["end_path_location"]

    # Dividing the task into 2 (halfway)
    if not task["halfway"]: # AGV has completed picking
        task = {
            "destination": start_path_location,
            "storage": start_pallet_location,
            "action": 2,
        }
        return task
    else:
        task = {
            "destination": end_path_location,
            "storage": end_pallet_location,
            "action": 3,
        }
        return task


def assign_task_to_agv():
    from server.agv.col_avoid import agvs_data
    from server.agv.scheduler import working_agvs

    # agvs_data = Get_values_from_agv_json()
    agvs = list(agvs_data.keys())
    # working_agvs = Get_values_from_working_agvs_json()
    if not agvs:
        return None
    else:
        available_agvs = [agv for agv in agvs if (agv not in working_agvs.keys() and agv not in permanent_obstacles.keys())]    
        if not available_agvs:
            return None
        print("Available AGVs: " + str(available_agvs))
        agv_id = random.choice(available_agvs)

    task = generate_random_task()
    task["assigned_agv"] = agv_id
    working_agvs[agv_id] = task
    # Update_working_agvs_json(working_agvs)
    sending_task = task_divider(task)

    topic = f"{agv_id}/goal"
    message_dict = sending_task
    message_json = json.dumps(message_dict)
    mqtt_client.publish(topic, message_json, qos=2)
    print("Loading task" + message_json + " assigned to " + agv_id)


# Task scheduler to assign tasks to AGVs at regular intervals
def run_task_scheduler(interval):
    def task_scheduler():
        print("Task scheduler started")
        while True:
            assign_task_to_agv()
            time.sleep(interval)

    thread = threading.Thread(target=task_scheduler)
    thread.daemon = True
    thread.start()


def task_complete(data):
    from server.agv.scheduler import working_agvs

    agv_id = data["agv_id"]
    # working_agvs = Get_values_from_working_agvs_json()
    if agv_id in working_agvs.keys():
        task = working_agvs[agv_id]
        if not task["halfway"]:
            working_agvs[agv_id]["halfway"] = True
            # Update_working_agvs_json(working_agvs)
            print("Loading task completed by " + agv_id)

            # sending_task = task_divider(task)
            # topic = f"{agv_id}/goal"
            # message_dict = sending_task
            # message_json = json.dumps(message_dict)
            # mqtt_client.publish(topic, message_json, qos=2)
            # print("Unloading task" + message_json + " assigned to " + agv_id)
        else:
            del working_agvs[agv_id]
            # working_agvs[agv_id] = None
            # Update_working_agvs_json(working_agvs)
            print("Unloading task completed by " + agv_id)
