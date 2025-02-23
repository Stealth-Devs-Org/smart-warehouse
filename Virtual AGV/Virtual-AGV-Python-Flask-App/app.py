import copy
import os
import threading
import time
import ujson as json
import yaml
from mqtt_handler import (
    ConnectMQTT,
    GetInterrupt,
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
    agv_state,
)

fixed_grid = None  # Global variable for the fixed grid
current_location = None


def read_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def ObtainGoal(idle_location):
    # ---------- print("Obtaining goal...")
    # goal = GetGoal()
    goal = ObtainGoalHttp(AGV_ID)
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
    # ---------- print("Returning goal...", destination, storage, action)
    return destination, storage, action


def MoveAGV(segments_list, destination, storage, action):
    waiting = 0
    
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
            
            if agv_state["current_status"] != 0:
                agv_state["current_status"] = 0
                UpdateCurrentLocation()

            path_clearance = RequestPathClearance(AGV_ID, segment)
            
            if (path_clearance) == 1: # No obstacles
                print("No obstacles in the segment",segment)
                waiting = 0
                if len(segment) != 1:
                    current_direction = SimulateTurning(AGV_ID, current_location, segment[1], current_direction, turning_time)
                    agv_state["current_direction"] = current_direction
                agv_state["current_status"] = 1
                UpdateCurrentLocation()
                
                for cell in segment:
                    if cell == agv_state["current_location"]:
                        continue
                    movement_time = 0
                    
                    while movement_time < cell_time:
                        interrupt_value = (
                            GetInterrupt()
                        )  # Fetch interrupt value using thread-safe method
                        #print(f"Current interrupt value: {interrupt_value}")

                        if interrupt_value == 1:
                            print("Stop signal received! Halting AGV.",time.time())
                            agv_state["current_status"] = 0
                            UpdateCurrentLocation()

                            time.sleep(interrupt_waiting_time)

                            SetInterrupt(0)
                            interrupted = 1

                        elif interrupt_value == 2:
                            print("Recalculate signal received!,",time.time())
                            
                            SetInterrupt(0)
                            interrupted = 1

                        if interrupted:
                            break
                        if agv_state["current_status"] != 1:
                            agv_state["current_status"] = 1
                            UpdateCurrentLocation()
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

            

            else:
                print("obstacles", path_clearance)
                if path_clearance == None:
                    print("No path clearance received. Retrying...")
                    return
                current_location_tuple = tuple(current_location)
                print("Recalculating path...")
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
                    print("waiting :", waiting)
                    if waiting < 2:
                        remain_path = [agv_state["current_segment"]] + segments[index + 1 :]
                        is_new_path_efficient, waiting_time = EvalNewPath(
                            new_segments, obstacles, remain_path, cell_time, turning_time
                        )
                        print("is_new_path_efficient:", is_new_path_efficient)
                        if not is_new_path_efficient:
                            waiting += 1
                            print("Waiting for obstacle to clear...waiting_time:", waiting_time)
                            time.sleep(waiting_time)
                            break
                        else:
                            recal_path = 1
                    else:
                        print("Waiting count exceeded. Use new path...")
                        recal_path = 1

                    if recal_path:
                        segments = new_segments
                        index = 0
                        break

    # ---------- print("End of path reached")
    agv_state["current_status"] = 0
    current_direction = SimulateEndAction(
        AGV_ID, current_location, current_direction, storage, action, turning_time
    )
    agv_state["current_direction"] = current_direction
    time.sleep(cell_time)


def send_keep_alive():
    while True:
        time.sleep(5)
        # ---------- print("Sending keep alive")
        UpdateCurrentLocation()


if __name__ == "__main__":

    #====================================Initialize AGV and Fixed Grid====================================#

    # Read configuration file
    config_path = os.getenv("CONFIG_PATH", "config.yaml")
    instance_id = int(os.getenv("INSTANCE_ID", "3"))

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
    agv_state["current_location"] = current_location
    agv_state["current_status"] = 0
    agv_state["current_segment"] = [agv_state["current_location"]]
    agv_state["current_direction"] = direction

    cell_time = cell_distance / speed
    interrupt_check_intervals = 200 # Per cell
    interrupt_waiting_time = cell_time*3

    # Read the grid from the Excel file
    grid_path = config["grid_path"]
    grid_size = 40  # Default grid size
    fixed_grid = ReadGrid(grid_path)

    # Create a copy of the fixed grid
    grid = copy.deepcopy(fixed_grid)

    #====================================Initialize MQTT Connection====================================#

    ConnectMQTT(AGV_ID)

    # Start the keep-alive thread
    # keep_alive_thread = threading.Thread(target=send_keep_alive)
    # keep_alive_thread.daemon = True
    # keep_alive_thread.start()

    while True:
        current_location = tuple(agv_state["current_location"])
        UpdateCurrentLocation()

        idle_time = 10  # Set the idle time in seconds before going to default location
        while idle_time > 0:
            destination, storage, action = ObtainGoal(idle_location)
            if destination != idle_location:
                break
            idle_time -= 0.5
            time.sleep(0.5)
        print("Destination:", destination, "Storage:", storage, "Action:", action)
        
        if (idle_location != current_location) or (destination != current_location):

            # Compute the path using D* Lite
            print("Current location:", current_location, "current_direction:", agv_state["current_direction"])
            path = CalculatePath(current_location, destination, grid)
            print("Path:", path)

            # Break the path into straight-line segments
            segments = CreateSegments(path)
            print("segments:", segments)

            # Display the path interactively
            MoveAGV(segments, destination, storage, action)
        else:
            # ---------- print("AGV is already at the destination")
            time.sleep(5)
