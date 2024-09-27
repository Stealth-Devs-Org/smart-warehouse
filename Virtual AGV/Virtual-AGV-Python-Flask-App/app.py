import copy
import os
import threading
import time

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
from server_communication import ObtainGoal, RequestPathClearance
from utils import CreateSegments, EvalNewPath, SimulateEndAction, SimulateTurning

fixed_grid = None  # Global variable for the fixed grid
global AGV_ID, speed, cell_distance, turning_time, direction, current_location, idle_location, status, current_segment
current_location = None
status = 0


def read_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def ObtainGoal(idle_location):
    print("Obtaining goal...")
    goal = GetGoal()
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
        action = 4
    print("Returning goal...", destination, storage, action)
    return destination, storage, action


def InteractivePathDisplay(segments_list, destination, direction, storage, action):
    global status, current_direction, current_location, current_segment
    previous_obstacles = None
    cell_time = cell_distance / speed
    current_direction = direction

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

                    movement_time = 0
                    is_path_correct = 1
                    while movement_time < cell_time:
                        while True:
                            interrupt_value = (
                                GetInterrupt()
                            )  # Fetch interrupt value using thread-safe method
                            print(f"Current interrupt value: {interrupt_value}")

                            if interrupt_value == 0:
                                break
                            elif interrupt_value == 1:
                                print("Stop signal received! Halting AGV.")
                                time.sleep(cell_time * 5)
                                if current_location in segment:
                                    current_segment = segment[segment.index(current_location) :]
                                    new_path_clearance = RequestPathClearance(
                                        AGV_ID, current_segment
                                    )
                                else:
                                    new_path_clearance = RequestPathClearance(AGV_ID, segment)
                                if (new_path_clearance) == 1:
                                    SetInterrupt(0)
                                    break
                                else:
                                    SetInterrupt(new_path_clearance)
                            else:
                                print("Recalculating path...")
                                print("Interrupt value:", interrupt_value)
                                is_path_correct = 0
                                if movement_time > 0:
                                    obstacles = [tuple(obstacle) for obstacle in interrupt_value]
                                    if cell not in obstacles:
                                        time.sleep(
                                            cell_time / 2
                                        )  # move forward for half the cell time
                                        movement_time += cell_time / 2
                                        current_location = cell
                                        current_segment = segment[segment.index(current_location) :]
                                    else:
                                        time.sleep(
                                            cell_time / 2
                                        )  # move reverse for half the cell time
                                        movement_time += cell_time / 2
                                new_path, obstacles = RecalculatePath(
                                    interrupt_value, current_location, destination, fixed_grid
                                )
                                if not new_path:
                                    print("No valid path found after recalculation.")
                                    SetInterrupt(0)
                                    return current_location, current_direction
                                else:
                                    print("New path:", new_path)
                                    print("Obstacles:", obstacles)

                                    new_segments = CreateSegments(new_path)
                                    UpdateCurrentLocation([current_location], AGV_ID, 0)

                                    segments = new_segments
                                    print("new_segments:", segments)
                                    index = 0
                                    SetInterrupt(0)
                                    break
                        if not is_path_correct:
                            break
                        time.sleep(cell_time / 2)
                        movement_time += cell_time / 2
                    if not is_path_correct:
                        is_path_correct = 1
                        break
                    current_location = cell
                    current_location_index = segment.index(current_location)
                    current_segment = segment[current_location_index:]
                    if current_location == destination:
                        status = 0
                        UpdateCurrentLocation(current_segment, AGV_ID, 0)
                    else:
                        status = 1
                        UpdateCurrentLocation(current_segment, AGV_ID, 1)

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
                        return current_location, current_direction
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

    print("End of path reached")
    SetGoal(None)
    status = action
    direction = SimulateEndAction(
        AGV_ID, current_location, current_direction, storage, action, turning_time
    )
    status = 0
    return current_location, direction


def send_keep_alive():
    global current_location, status, current_segment
    while True:
        time.sleep(10)
        print("Sending keep alive")
        UpdateCurrentLocation(current_segment, AGV_ID, status)


# Start the keep-alive thread
keep_alive_thread = threading.Thread(target=send_keep_alive)
keep_alive_thread.daemon = True
keep_alive_thread.start()


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
    current_segment = [current_location]

    """port = 501
    AGV_ID = 1
    speed = 2  # Speed of the AGV
    cell_distance = 2  # cell_distance between two cells
    turning_time = 2  # Time taken to turn the AGV in 45 degrees
    direction = "N"  # Initial direction of the AGV
    current_location = (36, 13)
    idle_location = (36, 13)
    threading.Thread(target=lambda: app.run(port=port)).start()"""

    ConnectMQTT(AGV_ID)

    # Read the grid from the Excel file
    grid_path = config["grid_path"]
    grid_size = 40  # Default grid size
    fixed_grid = ReadGrid(grid_path)

    # Create a copy of the fixed grid
    grid = copy.deepcopy(fixed_grid)

    UpdateCurrentLocation(current_segment, AGV_ID, 0)

    while True:
        idle_time = 0
        while idle_time < 10:
            destination, storage, action = ObtainGoal(idle_location)
            if destination != idle_location:
                break
            idle_time += 0.5
            time.sleep(0.5)

        print("Destination:", destination, "Storage:", storage, "Action:", action)
        print("Current location:", current_location)
        if (idle_location != current_location) or (destination != current_location):
            print("Current location is not the destination")

            # Compute the path using D* Lite
            path = CalculatePath(current_location, destination, grid)
            print("Path:", path)

            # Break the path into straight-line segments
            segments = CreateSegments(path)
            print("segments:", segments)

            # Display the path interactively
            current_location, direction = InteractivePathDisplay(
                segments, destination, direction, storage, action
            )
        else:
            print("AGV is already at the destination")
            time.sleep(5)

        time.sleep(1)
