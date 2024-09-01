import yaml
import threading
import copy
import matplotlib.pyplot as plt
import time
import os
from pathfinding import ReadGrid, CalculatePath, RecalculatePath
from visualization import PlotGrid
from server_communication import RequestPathClearance, ObtainGoal
from utils import CreateSegments, SimulateLoadingUnloading, SimulateTurning
from mqtt_handler import ConnectMQTT, UpdateCurrentLocation, GetInterrupt, SetInterrupt
from flask import Flask

app = Flask(__name__)

fixed_grid = None  # Global variable for the fixed grid
global AGV_ID
current_location = None

def read_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def InteractivePathDisplay(segments_list, current_location, goal, ax, direction):
    current_direction = direction
    plt.ion()  # Ensure interactive mode is on
    segments = segments_list.copy()
    index = 0
    while index < len(segments):
        segment = segments[index]
        while True:
            path_clearance = RequestPathClearance(AGV_ID, segment)

            if path_clearance == '1':
                print(f"Proceeding to the segment from {current_location} to {segment[-1]}")
                if segment == segments[0]:
                    current_direction = SimulateTurning(current_location, segment[0], current_direction, turning_time)
                for cell in segment:
                    if segment != segments[0] and cell == segment[1]:
                        print(f"Current location: {current_location}, next location: {segment[1]}")
                        current_direction = SimulateTurning(current_location, segment[1], current_direction, turning_time)
                    cell_time = cell_distance / speed
                    movement_time = 0
                    is_path_correct = 1
                    while movement_time < cell_time:
                        while True:
                            interrupt_value = GetInterrupt()  # Fetch interrupt value using thread-safe method
                            print(f"Current interrupt value: {interrupt_value}")
                            
                            if interrupt_value == 0:
                                break
                            elif interrupt_value == 1:
                                time.sleep(2)
                                print("Stop signal received! Halting AGV.")
                            else:
                                print("Recalculating path...")
                                is_path_correct = 0
                                new_path, obstacles = RecalculatePath(interrupt_value, current_location, goal, fixed_grid)
                                if not new_path:
                                    print("No valid path found after recalculation.")
                                    return
                                else:
                                    if movement_time > 0:
                                        time.sleep(cell_time/2) # move forward or reverse for half the cell time
                                        if cell in new_path:
                                            current_location = cell
                                            new_path = new_path[new_path.index(cell):]   
                                    print("New path:", new_path)
                                    print("Obstacles:", obstacles)
                                    
                                    new_segments = CreateSegments(new_path)
                                    
                                    ax.clear()  # Clear the previous plot
                                    PlotGrid(ax, grid_size, current_location, goal, new_path, obstacles, fixed_grid)
                                    ax.figure.canvas.draw()  # Redraw the canvas
                                    plt.pause(0.001)

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
                    UpdateCurrentLocation(current_location)
                else:
                    index += 1
                break

            elif path_clearance == '2':
                print("Pausing...")
                continue

            else:
                try:
                    new_path, obstacles = RecalculatePath(path_clearance, current_location, goal, fixed_grid)
                    if not new_path:
                        print("No valid path found after recalculation.")
                        return
                    else:
                        print("New path:", new_path)
                        
                        new_segments = CreateSegments(new_path)
                        
                        ax.clear()  # Clear the previous plot
                        PlotGrid(ax, grid_size, current_location, goal, new_path, obstacles, fixed_grid)
                        ax.figure.canvas.draw()  # Redraw the canvas
                        plt.pause(0.001)

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
    grid_size = 32  # Default grid size
    fixed_grid = ReadGrid(grid_path)

    # Create a copy of the fixed grid
    grid = copy.deepcopy(fixed_grid)

    while True:
        goal = ObtainGoal(AGV_ID)

        # Compute the path using D* Lite
        path = CalculatePath(current_location, goal, grid)
        print("Path:", path)

        # Initialize the plot
        fig, ax = plt.subplots(figsize=(10, 10))

        plt.ion()  # Turn on interactive mode

        # Plot the initial grid with the first path
        PlotGrid(ax, grid_size, current_location, goal, path, None, fixed_grid)
        plt.pause(0.001)

        # Show the initial plot
        plt.show(block=False)

        # Break the path into straight-line segments
        segments = CreateSegments(path)
        print("segments:", segments)

        # Display the path interactively
        current_location = InteractivePathDisplay(segments, current_location, goal, ax, direction)

        # Close the plot
        plt.close(fig)