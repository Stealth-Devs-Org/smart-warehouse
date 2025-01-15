import copy
import os
import threading
import time

# import ujson as json
import yaml

from mqtt_handler import (
    ConnectMQTT,
    GetGoal,
    GetInterrupt,
    SetGoal,
    SetInterrupt,
    UpdateCurrentLocation,
)
from pathfinding import CalculatePath, ReadGrid, RecalculatePath
from server_communication import ObtainGoalHttp, RequestPathClearance
from utils import (
    CreateSegments,
    EvalNewPath,
    SimulateEndAction,
    SimulateTurning,
    Update_agv_json,
    agv_state,
)

fixed_grid = None  # Global variable for the fixed grid
current_location = None


def read_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def ObtainGoal(idle_location):
    print("Obtaining goal...")
    # goal = GetGoal()
    goal = ObtainGoalHttp(AGV_ID)
    if goal is None:
        print("Goal not found. Returning default goal.")
        return idle_location, None, 0
    print("Goal:", goal)
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
        action = 0
    print("Returning goal...", destination, storage, action)
    return destination, storage, action


def InteractivePathDisplay(segments_list, destination, storage, action):
    previous_obstacles = None
    cell_time = cell_distance / speed
    current_direction = agv_state["current_direction"]
    current_location = agv_state["current_location"]

    segments = segments_list.copy()
    index = 0
    while index < len(segments):
        segment = segments[index]
        agv_state["current_segment"] = segment

        while True:
            interrupted = 0
            segment = agv_state["current_segment"]
            path_clearance = RequestPathClearance(AGV_ID, segment)
            # time.sleep(1)

            if (path_clearance) == 1:
                previous_obstacles = None
                print(f"Proceeding to the segment from {current_location} to {segment[-1]}")
                current_direction = SimulateTurning(
                    AGV_ID, current_location, segment[0], current_direction, turning_time
                )
                agv_state["current_direction"] = current_direction
                agv_state["current_status"] = 1
                UpdateCurrentLocation()

                for cell in segment:

                    if len(segment) > 1 and cell == segment[1]:
                        print(f"Current location: {current_location}, next location: {cell}")
                        current_direction = SimulateTurning(
                            AGV_ID, current_location, cell, current_direction, turning_time
                        )
                        agv_state["current_direction"] = current_direction
                        agv_state["current_status"] = 1

                    movement_time = 0
                    interrupt_check_intervals = 100
                    while movement_time < cell_time:
                        interrupt_value = (
                            GetInterrupt()
                        )  # Fetch interrupt value using thread-safe method
                        # print(f"Current interrupt value: {interrupt_value}")

                        if interrupt_value == 1:
                            print("Stop signal received! Halting AGV.")
                            agv_state["current_status"] = 0
                            UpdateCurrentLocation()

                            time.sleep(cell_time * 7)

                            SetInterrupt(0)
                            interrupted = 1

                        elif interrupt_value == 2:
                            print("Recalculating path...")
                            print("Interrupt value:", interrupt_value)
                            agv_state["current_status"] = 0
                            UpdateCurrentLocation()

                            time.sleep(cell_time)

                            SetInterrupt(0)
                            interrupted = 1

                        if interrupted:
                            break
                        time.sleep(cell_time / interrupt_check_intervals)
                        movement_time += cell_time / interrupt_check_intervals

                    if interrupted:
                        break

                    current_location = cell
                    agv_state["current_location"] = current_location
                    current_location_index = segment.index(current_location)
                    agv_state["current_segment"] = segment[current_location_index:]
                    agv_state["current_status"] = 1
                    UpdateCurrentLocation()

                else:
                    index += 1
                    break

            elif path_clearance == 0:
                UpdateCurrentLocation()
                time.sleep(cell_time)

            else:
                print("obstacle*", path_clearance)
                if path_clearance == None:
                    print("No path clearance received. Retrying...")
                    return
                current_location_tuple = tuple(current_location)
                new_path, obstacles = RecalculatePath(
                    (path_clearance), current_location_tuple, destination, fixed_grid
                )
                if not new_path:
                    print("No valid path found after recalculation.")
                    time.sleep(cell_time * 1)
                else:
                    recal_path = 0
                    print("New path:", new_path)
                    new_segments = CreateSegments(new_path)
                    print("previous_obstacles:", previous_obstacles)
                    print("obstacles:", obstacles)
                    if obstacles != previous_obstacles:
                        remain_path = [agv_state["current_segment"]] + segments[index + 1 :]
                        is_new_path_efficient, waiting_time = EvalNewPath(
                            new_segments, obstacles, remain_path, cell_time, turning_time
                        )
                        print("is_new_path_efficient:", is_new_path_efficient)
                        print("waiting_time:", waiting_time)
                        if not is_new_path_efficient:
                            previous_obstacles = obstacles
                            print("Waiting for obstacle to clear...", time.time())
                            agv_state["current_status"] = 9  # Waiting for obstacle to clear
                            UpdateCurrentLocation()
                            time.sleep(waiting_time)
                            print("Obstacle assumed cleared!", time.time())
                            break
                        else:
                            recal_path = 1
                    else:
                        recal_path = 1

                    if recal_path:
                        segments = new_segments
                        index = 0
                        break

    print("End of path reached")
    agv_state["current_status"] = 0
    SetGoal(None)
    current_direction = SimulateEndAction(
        AGV_ID, current_location, current_direction, storage, action, turning_time
    )
    agv_state["current_direction"] = current_direction
    time.sleep(cell_time)


def send_keep_alive():
    while True:
        time.sleep(5)
        print("Sending keep alive")
        UpdateCurrentLocation()


if __name__ == "__main__":
    # Read configuration file
    config_path = os.getenv("CONFIG_PATH", "config.yaml")
    instance_id = int(os.getenv("INSTANCE_ID", "2"))

    # Load configurations
    config = read_config(config_path)["instances"][instance_id]

    port = config["port"]
    AGV_ID = config["AGV_ID"]
    speed = config["speed"]  # Speed of the AGV
    cell_distance = config["cell_distance"]  # cell_distance between two cells
    turning_time = config["turning_time"]  # Time taken to turn the AGV in 45 degrees
    direction = config["direction"]  # Initial direction of the AGV
    current_location = tuple(config["current_location"])
    idle_location = tuple(config["idle_location"])

    agv_state["agv_id"] = AGV_ID
    agv_state["current_location"] = config["current_location"]
    agv_state["current_status"] = 0
    agv_state["current_segment"] = [agv_state["current_location"]]
    agv_state["current_direction"] = direction

    ConnectMQTT(AGV_ID)

    # Read the grid from the Excel file
    grid_path = config["grid_path"]
    grid_size = 40  # Default grid size
    fixed_grid = ReadGrid(grid_path)

    # Create a copy of the fixed grid
    grid = copy.deepcopy(fixed_grid)

    # Start the keep-alive thread
    # keep_alive_thread = threading.Thread(target=send_keep_alive)
    # keep_alive_thread.daemon = True
    # keep_alive_thread.start()

    while True:
        idle_time = 10  # Set the idle time in seconds before going to default location
        UpdateCurrentLocation()
        while idle_time > 0:
            destination, storage, action = ObtainGoal(idle_location)
            if destination != idle_location:
                break
            idle_time -= 0.5
            time.sleep(0.5)

        print("Destination:", destination, "Storage:", storage, "Action:", action)
        current_location = tuple(agv_state["current_location"])
        if (idle_location != current_location) or (destination != current_location):
            print("Current location is not the destination")

            # Compute the path using D* Lite
            path = CalculatePath(current_location, destination, grid)
            print("Path:", path)

            # Break the path into straight-line segments
            segments = CreateSegments(path)
            print("segments:", segments)

            # Display the path interactively
            InteractivePathDisplay(segments, destination, storage, action)
        else:
            print("AGV is already at the destination")
            time.sleep(5)
