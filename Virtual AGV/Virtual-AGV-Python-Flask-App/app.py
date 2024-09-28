import os
import threading
import time

import ujson as json
import yaml

from mqtt_handler import ConnectToMQTT, UpdateCurrentLocation
from pathfinding import ReadGrid
from utils import (
    CreateSegments,
    EvalNewPath,
    Get_values_from_agv_json,
    SimulateEndAction,
    SimulateTurning,
    Update_agv_json,
)

# Read configuration file
config_path = os.getenv("CONFIG_PATH", "config.yaml")
instance_id = int(os.getenv("INSTANCE_ID", "0"))


def read_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# Load configurations
config = read_config(config_path)["instances"][instance_id]


def SetGoal(goal_local):
    file_name = f"agv{config["AGV_ID"]}_status.json"
    agv_state = {}
    agv_state["goal"] = goal_local
    Update_agv_json(file_name, agv_state)


def StopTask(wait_time=0):
    print("Stopping task...")
    file_name = f"agv{config["AGV_ID"]}_status.json"
    agv_state = {}
    agv_state["interrupt"] = 1
    agv_state["status"] = 0
    Update_agv_json(file_name, agv_state)

    task_thread.join()
    time.sleep(wait_time)
    agv_state["interrupt"] = 0
    Update_agv_json(file_name, agv_state)
    StartTaskInThread()


def StartTask():
    print("Starting task...")

    AGV_ID = config["AGV_ID"]
    file_name = f"agv{AGV_ID}_status.json"
    agv_state = Get_values_from_agv_json(file_name, 
        [
            "current_location",
            "current_segment",
            "current_status",
            "goal",
            "idle_location",
        ]
    )
    current_location = agv_state["current_location"]
    current_segment = agv_state["current_segment"]
    current_status = agv_state["current_status"]

    grid_path = config["grid_path"]

    from pathfinding import CalculatePath

    UpdateCurrentLocation(AGV_ID, current_location, current_segment, current_status)

    # Create a copy of the fixed grid
    grid = ReadGrid(grid_path)

    destination = None
    goal = agv_state["goal"]
    if goal:
        destination = tuple(map(int, goal.get("destination")))
        if goal.get("storage"):
            storage = tuple(map(int, goal.get("storage")))
        else:
            storage = None

        action = goal.get("action")  # 0: idle, 2: load, 3: unload, 4: charge
    else:
        idle_location_tuple = tuple(agv_state["idle_location"])
        destination = idle_location_tuple
        storage = None
        action = 4

    current_location_tuple = tuple(current_location)
    interrupt = 0
    while interrupt == 0:
        if destination != current_location_tuple:

            # Compute the path using D* Lite
            path = CalculatePath(current_location_tuple, destination, grid)
            print("Path:", path)

            # Break the path into straight-line segments
            segments = CreateSegments(path)
            print("segments:", segments)

            current_location, current_direction, interrupt = InteractivePathDisplay(
                segments, destination, storage, action, grid
            )
            
            current_location_tuple = tuple(current_location)
        else:
            print("AGV is already at the destination")
            break


def StartTaskInThread():
    global task_thread
    task_thread = threading.Thread(target=StartTask)
    task_thread.start()


def InteractivePathDisplay(segments_list, destination, storage, action, grid):
    from pathfinding import RecalculatePath
    from server_communication import RequestPathClearance

    AGV_ID = config["AGV_ID"]
    file_name = f"agv{AGV_ID}_status.json"
    agv_state = Get_values_from_agv_json(file_name, 
        [
            "speed",
            "cell_distance",
            "turning_time",
            "current_location",
            "current_segment",
            "current_direction",
            "previous_obstacles",
            "interrupt",
        ]
    )
    speed = agv_state["speed"]
    cell_distance = agv_state["cell_distance"]
    turning_time = agv_state["turning_time"]
    current_location = agv_state["current_location"]
    current_segment = agv_state["current_segment"]
    current_direction = agv_state["current_direction"]
    previous_obstacles = agv_state["previous_obstacles"]
    interrupt = agv_state["interrupt"]
    FIXED_GRID = grid
    file_name = f"agv{AGV_ID}_status.json"

    cell_time = cell_distance / speed

    segments = segments_list.copy()
    index = 0
    while index < len(segments):
        segment = segments[index]

        while True:

            path_clearance = RequestPathClearance(AGV_ID, segment)

            if (path_clearance) == 1:
                agv_state["previous_obstacles"] = None
                print(f"Proceeding to the segment from {current_location} to {segment[-1]}")
                for cell in segment:
                    print(f"Current location: {current_location}, next location: {cell}")
                    current_direction = SimulateTurning(
                        current_location, cell, current_direction, turning_time
                    )

                    # Interrupt check
                    move_time = cell_time
                    check_intervals = 1000
                    sleep_time = move_time / check_intervals
                    while move_time > 0:
                        interrupt = Get_values_from_agv_json(file_name, ["interrupt"]).get("interrupt")
                        if interrupt == 1:
                            print("Interrupted!")
                            return current_location, current_direction, 1
                        time.sleep(sleep_time)
                        move_time -= sleep_time

                    current_location = cell
                    current_location_index = segment.index(current_location)
                    current_segment = segment[current_location_index:]
                    if current_location == destination:
                        current_status = 0
                    else:
                        current_status = 1
                    UpdateCurrentLocation(AGV_ID, current_location, current_segment, current_status)
                    agv_state["current_location"] = current_location
                    agv_state["current_segment"] = current_segment
                    agv_state["current_status"] = current_status
                    Update_agv_json(file_name, agv_state)

                else:
                    index += 1
                break

            else:
                print("obstacle*", path_clearance)
                obstacles = path_clearance
                current_location_tuple = tuple(current_location)
                new_path = RecalculatePath(
                    obstacles, current_location_tuple, destination, FIXED_GRID
                )
                if not new_path:
                    print("No valid path found after recalculation.")
                    return current_location, current_direction, 0
                else:
                    recal_path = 0
                    print("New path:", new_path)
                    new_segments = CreateSegments(new_path)
                    print("previous_obstacles:", previous_obstacles)
                    print("obstacles:", obstacles)
                    if obstacles != previous_obstacles:
                        remain_path = segments[index:]
                        is_new_path_efficient, waiting_time = EvalNewPath(
                            new_segments, obstacles, remain_path, cell_time, turning_time
                        )
                        print("is_new_path_efficient:", is_new_path_efficient)
                        print("waiting_time:", waiting_time)
                        if not is_new_path_efficient:
                            previous_obstacles = obstacles
                            print("Waiting for obstacle to clear...", time.time())
                            time.sleep(waiting_time)
                            print("Obstacle cleared!", time.time())
                            break
                        else:
                            recal_path = 1
                    else:
                        recal_path = 1

                    if recal_path:
                        segments = new_segments
                        index = 0
                        break
        time.sleep(0.5)

    print("End of path reached")
    agv_state["goal"] = None

    current_status = action
    UpdateCurrentLocation(AGV_ID, current_location, current_segment, current_status)
    agv_state["current_status"] = current_status
    Update_agv_json(file_name, agv_state)

    current_direction = SimulateEndAction(
        AGV_ID, current_location, current_direction, storage, action, turning_time
    )

    current_status = 0
    UpdateCurrentLocation(AGV_ID, current_location, current_segment, current_status)
    agv_state["current_status"] = current_status
    Update_agv_json(file_name, agv_state)

    # time.sleep(cell_time)
    return current_location, current_direction, 0


def send_keep_alive():
    while True:
        time.sleep(10)
        print("Sending keep alive")
        file_name = f"agv{config["AGV_ID"]}_status.json"
        agv_state = Get_values_from_agv_json(file_name, 
            ["current_location", "current_segment", "current_status", "goal"]
        )
        current_location = agv_state["current_location"]
        current_segment = agv_state["current_segment"]
        current_status = agv_state["current_status"]
        UpdateCurrentLocation(AGV_ID, current_location, current_segment, current_status)


if __name__ == "__main__":

    agv_state = {}
    AGV_ID = config["AGV_ID"]
    agv_state["agv_id"] = AGV_ID
    agv_state["speed"] = config["speed"]  # Speed of the AGV
    agv_state["cell_distance"] = config["cell_distance"]  # cell_distance between two cells
    agv_state["turning_time"] = config["turning_time"]  # Time taken to turn the AGV in 45 degrees
    agv_state["current_direction"] = config["direction"]  # Initial direction of the AGV
    agv_state["current_location"] = config["current_location"]
    agv_state["current_status"] = 0
    agv_state["current_segment"] = [agv_state["current_location"]]
    agv_state["idle_location"] = config["idle_location"]
    agv_state["previous_obstacles"] = []
    agv_state["interrupt"] = 0
    agv_state["goal"] = None

    file_name = f"agv{AGV_ID}_status.json"
    with open(file_name, "w") as f:
        json.dump({}, f)

    Update_agv_json(file_name, agv_state)

    ConnectToMQTT(AGV_ID)
    StartTask()

    # Start the keep-alive thread
    keep_alive_thread = threading.Thread(target=send_keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    try:
        while True:
            time.sleep(1)
            # current_location = Get_values_from_agv_json(["current_location"]).get(
            #     "current_location"
            # )
            # print("Current location:", current_location)
    except KeyboardInterrupt:
        print("Program terminated by user.")
