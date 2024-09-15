import json
import random
import threading
import time

from server.agv.col_avoid import agvs_data
from server.mqtt.utils import mqtt_client

inbound_pallet_locations = {}
outbound_pallet_locations = {}
storage_pallet_locations = {}

working_agvs = []

# Assigning pallet locations with respective path location
for y in range(5, 12):
    inbound_pallet_locations[(18, y)] = (17, y)
    inbound_pallet_locations[(19, y)] = (20, y)
    inbound_pallet_locations[(21, y)] = (20, y)
    inbound_pallet_locations[(22, y)] = (23, y)
    outbound_pallet_locations[(25, y)] = (24, y)
    outbound_pallet_locations[(26, y)] = (27, y)
    outbound_pallet_locations[(28, y)] = (27, y)
    outbound_pallet_locations[(29, y)] = (30, y)

for x in range(11, 22):
    storage_pallet_locations[(x, 27)] = (x, 28)
    storage_pallet_locations[(x, 26)] = (x, 25)
    storage_pallet_locations[(x, 24)] = (x, 25)
    storage_pallet_locations[(x, 23)] = (x, 22)
    storage_pallet_locations[(x, 21)] = (x, 22)
    storage_pallet_locations[(x, 20)] = (x, 19)
    storage_pallet_locations[(x, 18)] = (x, 19)
    storage_pallet_locations[(x, 17)] = (x, 16)

for x in range(25, 36):
    storage_pallet_locations[(x, 27)] = (x, 28)
    storage_pallet_locations[(x, 26)] = (x, 25)
    storage_pallet_locations[(x, 24)] = (x, 25)
    storage_pallet_locations[(x, 23)] = (x, 22)
    storage_pallet_locations[(x, 21)] = (x, 22)
    storage_pallet_locations[(x, 20)] = (x, 19)
    storage_pallet_locations[(x, 18)] = (x, 19)
    storage_pallet_locations[(x, 17)] = (x, 16)


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
        "start_pallet_location": start_pallet_location,
        "start_path_location": start_path_location,
        "end_pallet_location": end_pallet_location,
        "end_path_location": end_path_location,
    }

    return task


def assign_task_to_agv():
    agvs = list(agvs_data.keys())
    if not agvs:
        return None
    agv_id = random.choice(agvs)
    while agv_id in working_agvs:
        agvs.remove(agv_id)
        if not agvs:
            return None
        agv_id = random.choice(agvs)

    task = generate_random_task()
    working_agvs.append(agv_id)

    topic = f"{agv_id}/goal"
    message_dict = task
    message_json = json.dumps(message_dict)
    mqtt_client.publish(topic, message_json, qos=2)


def run_task_scheduler(interval):
    def task_scheduler():
        while True:
            assign_task_to_agv()
            print("Task assigned to AGV")
            time.sleep(interval)

    thread = threading.Thread(target=task_scheduler)
    thread.start()


def task_complete(data):
    working_agvs.remove(data["agv_id"])
    assign_task_to_agv()
