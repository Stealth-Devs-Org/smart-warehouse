import yaml
import threading
import copy
import time
import os
from pathfinding import ReadGrid, CalculatePath, RecalculatePath
from server_communication import RequestPathClearance, ObtainGoal
from utils import CreateSegments, SimulateLoadingUnloading, SimulateTurning, EvalNewPath
from mqtt_handler import ConnectMQTT, UpdateCurrentLocation, GetInterrupt, SetInterrupt
from flask import Flask

app = Flask(__name__)

fixed_grid = None  # Global variable for the fixed grid
global AGV_ID
current_location = None

def read_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def InteractivePathDisplay(segments_list, current_location, goal, direction):
    previous_obstacles = None
    cell_time = cell_distance / speed
    current_direction = direction
    
    segments = segments_list.copy()
    index = 0
    while index < len(segments):
        segment = segments[index]
        
        while True:
            interrupt_value = GetInterrupt()
            path_clearance = RequestPathClearance(AGV_ID, segment)
            if path_clearance == '1':
                previous_obstacles = None
                print(f"Proceeding to the segment from {current_location} to {segment[-1]}")
                if segment == segments[0]:
                    current_direction = SimulateTurning(current_location, segment[0], current_direction, turning_time)
                for cell in segment:
                    if segment != segments[0] and len(segment)>1 and cell == segment[1]:
                        print(f"Current location: {current_location}, next location: {segment[1]}")
                        current_direction = SimulateTurning(current_location, segment[1], current_direction, turning_time)
                    
                    movement_time = 0
                    is_path_correct = 1
                    while movement_time < cell_time:
                        while True:
                            interrupt_value = GetInterrupt()  # Fetch interrupt value using thread-safe method
                            print(f"Current interrupt value: {interrupt_value}")
                            
                            if interrupt_value == 0:
                                break
                            elif interrupt_value == 1:
                                time.sleep(cell_time)
                                print("Stop signal received! Halting AGV.")
                            else:
                                print("Recalculating path...")
                                print("Interrupt value:", interrupt_value)
                                is_path_correct = 0
                                if movement_time > 0:
                                    obstacles = eval(interrupt_value)
                                    current_location_index = segment.index(current_location)
                                    if segment[current_location_index+1] not in obstacles:
                                        time.sleep(cell_time/2) # move forward for half the cell time
                                        movement_time += cell_time/2
                                        current_location = cell
                                    else:
                                        time.sleep(cell_time/2) # move reverse for half the cell time
                                        movement_time += cell_time/2
                                new_path, obstacles = RecalculatePath(interrupt_value, current_location, goal, fixed_grid)
                                if not new_path:
                                    print("No valid path found after recalculation.")
                                    break
                                else:   
                                    print("New path:", new_path)
                                    print("Obstacles:", obstacles)
                                    
                                    new_segments = CreateSegments(new_path)
                                    UpdateCurrentLocation([current_location],AGV_ID,0)
                                    
                                    
                                    segments = new_segments
                                    print("new_segments:", segments)
                                    index = 0
                                    SetInterrupt(0)
                                    break
                        if not is_path_correct:
                            break
                        time.sleep(cell_time/2)
                        movement_time += cell_time/2
                    if not is_path_correct:
                        is_path_correct = 1
                        break
                    current_location = cell
                    current_location_index = segment.index(current_location)
                    if current_location == goal:
                        UpdateCurrentLocation(segment[current_location_index:],AGV_ID,0)
                    else:
                        UpdateCurrentLocation(segment[current_location_index:],AGV_ID,1)
                    
                else:
                    index += 1
                break

            elif path_clearance == '2':
                print("Pausing...")
                time.sleep(cell_time)
                continue

            else:
                print("obstacle*",path_clearance)
                try:
                    new_path, obstacles = RecalculatePath(path_clearance, current_location, goal, fixed_grid)
                    if not new_path:
                        print("No valid path found after recalculation.")
                        break
                    else:
                        recal_path = 0
                        print("New path:", new_path)
                        new_segments = CreateSegments(new_path)
                        print("previous_obstacles:",previous_obstacles)
                        print("obstacles:",obstacles)
                        if obstacles != previous_obstacles:
                            remain_path = segments[index:]
                            is_new_path_efficient,waiting_time = EvalNewPath(new_segments,obstacles,remain_path,cell_time,turning_time)
                            print("is_new_path_efficient:",is_new_path_efficient)
                            print("waiting_time:",waiting_time)
                            if not is_new_path_efficient:
                                previous_obstacles = obstacles
                                print("Waiting for obstacle to clear...",time.time())
                                time.sleep(waiting_time)
                                print("Obstacle cleared!",time.time())
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
    SimulateLoadingUnloading(current_location)
    return current_location

if __name__ == '__main__':
    # Read configuration file
    config_path = os.getenv('CONFIG_PATH', 'config.yaml')
    instance_id = int(os.getenv('INSTANCE_ID', '0'))

    # Load configurations
    config = read_config(config_path)["instances"][instance_id]

    port = config["port"]
    AGV_ID = config["AGV_ID"]
    speed = config["speed"]  # Speed of the AGV
    cell_distance = config["cell_distance"]  # cell_distance between two cells
    turning_time = config["turning_time"]  # Time taken to turn the AGV in 45 degrees
    direction = config["direction"]  # Initial direction of the AGV
    current_location = tuple(config["current_location"])

    threading.Thread(target=lambda: app.run(port=port)).start()

    ConnectMQTT(AGV_ID)

    # Read the grid from the Excel file
    grid_path = config["grid_path"]
    grid_size = 40  # Default grid size
    fixed_grid = ReadGrid(grid_path)

    # Create a copy of the fixed grid
    grid = copy.deepcopy(fixed_grid)

    while True:
        goal = ObtainGoal(AGV_ID)

        # Compute the path using D* Lite
        path = CalculatePath(current_location, goal, grid)
        print("Path:", path)

        # Break the path into straight-line segments
        segments = CreateSegments(path)
        print("segments:", segments)

        # Display the path interactively
        current_location = InteractivePathDisplay(segments, current_location, goal, direction)