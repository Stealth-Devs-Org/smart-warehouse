import copy
import ctypes
import os
import threading
import time

import yaml

from pathfinding import ReadGrid
from utils import (
    CreateSegments,
    EvalNewPath,
    SimulateEndAction,
    SimulateTurning,
    Update_agv_json,
)

# Read configuration file
config_path = os.getenv("CONFIG_PATH", "config.yaml")
instance_id = int(os.getenv("INSTANCE_ID", "2"))


def read_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# Load configurations
config = read_config(config_path)["instances"][instance_id]

AGV_ID = config["AGV_ID"]
speed = config["speed"]  # Speed of the AGV
cell_distance = config["cell_distance"]  # cell_distance between two cells
turning_time = config["turning_time"]  # Time taken to turn the AGV in 45 degrees
current_direction = config["direction"]  # Initial direction of the AGV
current_location = tuple(config["current_location"])
status = 0
current_segment = current_location
idle_location = tuple(config["idle_location"])
previous_obstacles = []
interrupt = 0
goal = None

grid_path = config["grid_path"]
fixed_grid = ReadGrid(grid_path)

from mqtt_handler import UpdateCurrentLocation


def SetGoal(goal_local):
    global goal
    goal = goal_local


def StopTask():
    print("Stopping task...")
    global interrupt, status
    interrupt = 1
    status = 0


def StartTask():
    print("Starting task...")
    from pathfinding import CalculatePath

    global current_location, status

    UpdateCurrentLocation(AGV_ID, current_location, [current_location], status)

    # Create a copy of the fixed grid
    grid = copy.deepcopy(fixed_grid)

    global goal
    if goal:
        destination = tuple(map(int, goal.get("destination")))
        if goal.get("storage"):
            storage = tuple(map(int, goal.get("storage")))
        else:
            storage = None

        action = goal.get("action")  # 0: idle, 2: load, 3: unload, 4: charge
    else:
        destination = idle_location
        storage = None
        action = 4

    if destination != current_location:

        # Compute the path using D* Lite
        path = CalculatePath(current_location, destination, grid)
        print("Path:", path)

        # Break the path into straight-line segments
        segments = CreateSegments(path)
        print("segments:", segments)

        global current_direction
        current_location, current_direction = InteractivePathDisplay(
            segments, destination, storage, action
        )
    else:
        print("AGV is already at the destination")


def StartTaskInThread():
    task_thread = threading.Thread(target=StartTask)
    task_thread.start()


def InteractivePathDisplay(segments_list, destination, storage, action):
    from pathfinding import RecalculatePath
    from server_communication import RequestPathClearance

    global previous_obstacles, current_direction, current_location, interrupt, goal, status

    cell_time = cell_distance / speed

    segments = segments_list.copy()
    index = 0
    while index < len(segments):
        segment = segments[index]

        while True:

            path_clearance = RequestPathClearance(AGV_ID, segment)

            if (path_clearance) == 1:
                previous_obstacles = None
                print(f"Proceeding to the segment from {current_location} to {segment[-1]}")
                for cell in segment:
                    print(f"Current location: {current_location}, next location: {cell}")
                    current_direction = SimulateTurning(
                        current_location, cell, current_direction, turning_time
                    )
                    if interrupt == 1:
                        time.sleep(cell_time * 3)
                        return current_location, current_direction
                    time.sleep(cell_time)  # This is the time taken to move from one cell to another
                    current_location = cell
                    current_location_index = segment.index(current_location)
                    if current_location == destination:
                        status = 0
                        UpdateCurrentLocation(
                            AGV_ID, current_location, segment[current_location_index:], status
                        )
                    else:
                        status = 1
                        UpdateCurrentLocation(
                            AGV_ID, current_location, segment[current_location_index:], status
                        )

                else:
                    index += 1
                break

            else:
                print("obstacle*", path_clearance)
                obstacles = path_clearance
                new_path = RecalculatePath(obstacles, current_location, destination, fixed_grid)
                if not new_path:
                    print("No valid path found after recalculation.")
                    break
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
        time.sleep(1)

    print("End of path reached")
    goal = None
    current_direction = SimulateEndAction(
        AGV_ID, current_location, current_direction, storage, action, turning_time
    )
    time.sleep(cell_time)
    return current_location, current_direction


def send_keep_alive():
    global current_location, status
    while True:
        time.sleep(10)
        print("Sending keep alive")
        UpdateCurrentLocation([current_location], AGV_ID, status)


# Start the keep-alive thread
keep_alive_thread = threading.Thread(target=send_keep_alive)
keep_alive_thread.daemon = True
keep_alive_thread.start()


if __name__ == "__main__":
    StartTask()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")
