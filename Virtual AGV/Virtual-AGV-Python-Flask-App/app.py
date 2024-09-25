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
instance_id = int(os.getenv("INSTANCE_ID", "0"))


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
idle_location = tuple(config["idle_location"])
previous_obstacles = []
interrupt = 0

grid_path = config["grid_path"]
fixed_grid = ReadGrid(grid_path)

Update_agv_json(
    {
        "agv_id": AGV_ID,
        "status": 0,
        "location": current_location,
        "segment": current_location,
        "direction": current_direction,
    }
)

from mqtt_handler import GetGoal, SetGoal


def StopTask():
    print("Stopping task...")
    global interrupt
    interrupt = 1
    Update_agv_json(
        {
            "status": 0,
        }
    )


def StartTask():
    print("Starting task...")
    from pathfinding import CalculatePath

    # Create a copy of the fixed grid
    grid = copy.deepcopy(fixed_grid)

    goal = GetGoal()
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

    global current_location
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

    return Update_agv_json(
        {
            "location": current_location,
            "direction": current_direction,
        }
    )


def InteractivePathDisplay(segments_list, destination, storage, action):
    from pathfinding import RecalculatePath
    from server_communication import RequestPathClearance

    global previous_obstacles, current_direction, current_location, interrupt

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
                if segment == segments[0]:
                    current_direction = SimulateTurning(
                        current_location, segment[0], current_direction, turning_time
                    )
                for cell in segment:
                    if segment != segments[0] and len(segment) > 1 and cell == segment[1]:
                        print(f"Current location: {current_location}, next location: {segment[1]}")
                        current_direction = SimulateTurning(
                            current_location, segment[1], current_direction, turning_time
                        )
                    if interrupt == 1:
                        return current_location, current_direction
                    current_location = cell
                    current_location_index = segment.index(current_location)
                    if current_location == destination:
                        Update_agv_json(
                            {
                                "status": 0,
                                "location": current_location,
                                "segment": segment[current_location_index:],
                                "direction": current_direction,
                            }
                        )
                    else:
                        Update_agv_json(
                            {
                                "location": current_location,
                                "segment": segment[current_location_index:],
                                "status": 1,
                                "direction": current_direction,
                            }
                        )
                    time.sleep(cell_time)

                else:
                    index += 1
                break

            else:
                print("obstacle*", path_clearance)
                try:
                    new_path, obstacles = RecalculatePath(
                        (path_clearance), current_location, destination, fixed_grid
                    )
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

                except Exception as e:
                    print(f"Invalid input: {e}")
                    continue
        time.sleep(1)

    print("End of path reached")
    SetGoal(None)
    current_direction = SimulateEndAction(
        AGV_ID, current_location, current_direction, storage, action, turning_time
    )
    time.sleep(cell_time)
    return current_location, current_direction


if __name__ == "__main__":
    StartTask()
    while True:
        time.sleep(1)

    # def update_location_periodically(interval):
    #     updated_idle_location = False
    #     while True:
    #         with open("agv_status.json", "r") as f:
    #             agv_status = json.load(f)
    #             if agv_status["status"] == 0 and not updated_idle_location:
    #                 UpdateCurrentLocation()
    #                 updated_idle_location = True
    #             elif agv_status["status"] == 1:
    #                 UpdateCurrentLocation()
    #         time.sleep(interval)

    # # Start the periodic update in a separate thread
    # update_interval = config.get("update_interval", 0.25)  # Default interval is 5 seconds
    # update_thread = threading.Thread(target=update_location_periodically, args=(update_interval,))
    # update_thread.daemon = False
    # update_thread.start()
