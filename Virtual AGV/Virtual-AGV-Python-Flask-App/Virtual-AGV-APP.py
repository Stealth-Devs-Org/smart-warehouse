from flask import Flask,request, jsonify
import requests
import pandas as pd
import matplotlib.pyplot as plt
from queue import PriorityQueue
import copy
import time
import threading
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

# Shared variable to indicate stop signal
interrupt = 0

# MQTT setup
MQTT_BROKER = "test.mosquitto.org"  
MQTT_PORT = 1883
MQTT_TOPIC = "agv/location"


# Initialize MQTT client
mqtt_client = mqtt.Client()

def ConnectMQTT():
    # Connect to the MQTT broker
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()  # Start the MQTT loop in a separate thread
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")



@app.route('/interrupt', methods=['POST'])
def interrupt_route():
    print("Inturrupt occred")
    global interrupt
    data = request.json
    if data.get('interrupt')=='1':
        interrupt = 0
        return jsonify({'status': 'Resuming AGV'}), 200
    elif data.get('interrupt')=='2':
        interrupt = 1
        return jsonify({'status': 'Stopping AGV'}), 200
    else:
        interrupt = data.get('interrupt')
        print("Interrupt:",interrupt) 
        return jsonify({'status': 'Recalculate path'}), 200
    

# Define the fixed grid from the Excel file
def ReadGrid(file_path):

    # Function to split and clean the connected nodes and convert to tuples
    def process_connected_nodes(connected_nodes_str):
        connected_nodes_str = connected_nodes_str.strip()[1:-1]
        node_pairs = connected_nodes_str.split('),(')
        return [tuple(map(int, pair.split(','))) for pair in node_pairs]
    
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Initialize the grid dictionary
    fixed_grid = {}

    # Iterate over each row, process and populate the grid dictionary
    for index, row in df.iterrows():
        node = tuple(map(int, row['Node'].strip('()').split(',')))
        connected_nodes_list = process_connected_nodes(row['Connected Nodes'])
        fixed_grid[node] = connected_nodes_list

    return fixed_grid



# Function to calculate the path from start to goal
def CalculatePath(start, goal, grid):
    # Define the D* Lite algorithm with heuristic, starting from the goal
    def heuristic(a, b):
        # Manhattan distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_list = PriorityQueue()
    g_score = {node: float('inf') for node in grid.keys()}
    rhs = {node: float('inf') for node in grid.keys()}
    
    # Start at the goal
    g_score[goal] = float('inf')
    rhs[goal] = 0
    open_list.put((heuristic(start, goal), goal))

    def calculate_key(node):
        return min(g_score[node], rhs[node]) + heuristic(start, node)

    came_from = {}

    while not open_list.empty():
        current = open_list.get()[1]

        if g_score[current] > rhs[current]:
            g_score[current] = rhs[current]
            for neighbor in grid.get(current, []):
                tentative_rhs = g_score[current] + 1  # Assuming uniform cost
                if tentative_rhs < rhs.get(neighbor, float('inf')):
                    rhs[neighbor] = tentative_rhs
                    came_from[neighbor] = current
                    open_list.put((calculate_key(neighbor), neighbor))
        else:
            g_score[current] = float('inf')
            for neighbor in grid.get(current, []):
                if came_from.get(neighbor) == current:
                    rhs[neighbor] = min([g_score[n] + 1 for n in grid.get(neighbor, [])])
                    open_list.put((calculate_key(neighbor), neighbor))

    # Reconstruct path from start to goal
    path = []
    node = start
    while node != goal:
        path.append(node)
        if node not in came_from:
            return []  # Return empty path if no valid path exists
        node = came_from[node]
    path.append(goal)
    return path

# Function to plot the grid and path
def PlotGrid(ax, grid_size, start=None, goal=None, path=None, obstacles=None):
    ax.clear()  # Clear the current plot

    # Plot main grid lines (dashed)
    for x in range(grid_size + 1):
        ax.axhline(y=x, color='gray', linestyle='--', linewidth=0.5)
        ax.axvline(x=x, color='gray', linestyle='--', linewidth=0.5)

    # Plot additional grid lines (solid)
    for x in range(grid_size):
        ax.axhline(y=x + 0.5, color='lightgray', linestyle='-', linewidth=0.5)
        ax.axvline(x=x + 0.5, color='lightgray', linestyle='-', linewidth=0.5)

    # Plot connections
    for (x, y), connections in grid.items():
        for (cx, cy) in connections:
            if 0 <= cx <= grid_size and 0 <= cy <= grid_size:
                ax.plot([x, cx], [y, cy], 'ro-', markersize=5)  # Red lines with circle markers

    # Plot the path
    if path:
        for i in range(len(path) - 1):
            x0, y0 = path[i]
            x1, y1 = path[i + 1]
            ax.plot([x0, x1], [y0, y1], 'g-', linewidth=2)  # Green path

    # Plot start and end points
    if start:
        ax.plot(start[0], start[1], 'bo', markersize=10)  # Blue start point
    if goal:
        ax.plot(goal[0], goal[1], 'mo', markersize=10)  # Magenta goal point

    # Plot obstacles
    if obstacles:
        for obs in obstacles:
            ax.plot(obs[0], obs[1], 'ks', markersize=10)  # Black squares for obstacles

    # Set axis limits and labels
    ax.set_xlim(-1, grid_size + 1)
    ax.set_ylim(-1, grid_size + 1)
    ax.set_xticks(range(grid_size + 1))
    ax.set_yticks(range(grid_size + 1))
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    # Set y-ticks to match the descending axis
    ax.set_yticks(range(grid_size, -1, -1))
    ax.set_yticklabels(range(grid_size, -1, -1))

    ax.set_aspect('equal')
    ax.grid(True)
    plt.draw()  # Update the plot
    plt.pause(0.001)


# Function to break path into straight-line segments
def CreateSegments(path):
    segments = []
    if not path:
        return segments

    current_segment = [path[1]]
    direction = None
    for i in range(2, len(path)):
        if path[i][0] == current_segment[-1][0]:
            new_direction = 'vertical'
            if direction != new_direction:
                if direction:
                    segments.append(current_segment[0:-1])
                    current_segment = [current_segment[-1]]
                direction = new_direction
            current_segment.append(path[i])
        elif path[i][1] == current_segment[-1][1]:
            new_direction = 'horizontal'
            if direction != new_direction:
                if direction:
                    segments.append(current_segment[0:-1])
                    current_segment = [current_segment[-1]]
                direction = new_direction
            current_segment.append(path[i])
    segments.append(current_segment)
    return segments

# Function for simulate loading and unloading
def SimulateLoadingUnloading(current_location):
    # Simulate loading and unloading at the current location
    print(f"Loading and unloading at location: {current_location}")
    time.sleep(2)  # Simulate loading and unloading time

# Function to update current location in Main server and publish to MQTT
def UpdateCurrentLocation(current_location):
    # Publish the current location to the MQTT topic
    try:
        location_data = {"current_location": current_location}
        mqtt_client.publish(MQTT_TOPIC, json.dumps(location_data))
        print(f"Published current location {current_location} to MQTT topic '{MQTT_TOPIC}'")
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")

    # Update the current location in the Main server
    print(f"Current location updated to: {current_location}")

# Function to request path clearance from the Main server
def RequestPathClearance(AGV_ID, segment):
    url = "http://127.0.0.1:5000/path_clearance"  # Replace with the actual URL of the target Flask application
    payload = {'AGV_ID': AGV_ID, 'segment': [segment[0], segment[-1]]}
    
    print(f"Requesting path clearance from {segment[0]} to {segment[-1]}...")

    # return input("Enter 1 to proceed, 2 to pause, or any other key to recalculate path: ")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Check for HTTP errors
        return response.text  # Return the response content
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining path clearance: {e}")
        return None  # or handle the error as needed
    


# Function to recalculate the path considering new obstacles
def RecalculatePath(obstacle, current_node, goal):
    grid = copy.deepcopy(fixed_grid)  # Reset the grid to the original state
    obstacles = eval(obstacle)
    # Update grid to remove connections for new obstacles
    for obs in obstacles:
        grid.pop(obs, None)
        for node, connections in grid.items():
            if obs in connections:
                grid[node].remove(obs)
                    
    # Recalculate path from the current node
    new_path = CalculatePath(current_node, goal, grid)
    return new_path, obstacles

def ObtainGoal(AGV_ID):
    url = "http://127.0.0.1:5000/get_goal"  # Replace with the actual URL of the target Flask application
    payload = {'AGV_ID': AGV_ID}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        goal = tuple(map(int, response.json().get('goal')))
        return goal
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining goal: {e}")
        return None  # or handle the error as needed

# Reset the interrupt signal
def ResetInterrupt():    
    global interrupt
    interrupt = 0

# Function to handle interactive path display
def InteractivePathDisplay(segments_list, current_location, goal, ax):
    plt.ion()  # Ensure interactive mode is on
    segments = segments_list.copy()
    index = 0
    while index < len(segments):
        segment = segments[index]        
        while True:
            path_clearance = RequestPathClearance(AGV_ID, segment)

            if path_clearance == '1':
                print(f"Proceeding to the segment from {current_location} to {segment[-1]}")
                for cell in segment:
                    is_path_correct = 1
                    while True:
                        # Check for stop signal before moving to the next cell
                        if interrupt == 0:
                            break
                        elif interrupt == 1:
                            time.sleep(2)
                            print("Stop signal received! Halting AGV.")
                        else:
                            print("Recalculating path...")
                            is_path_correct = 0
                            new_path, obstacles = RecalculatePath(interrupt, current_location, goal)
                            if not new_path:
                                print("No valid path found after recalculation.")
                                return
                            else:
                                print("New path:", new_path)
                                print("Obstacles:", obstacles)
                                
                                # Break the new path into segments
                                new_segments = CreateSegments(new_path)
                                
                                # Plot the grid with the new path and obstacles
                                ax.clear()  # Clear the previous plot
                                PlotGrid(ax, grid_size, current_location, goal, new_path, obstacles)
                                ax.figure.canvas.draw()  # Redraw the canvas
                                plt.pause(0.001)

                                # Update segments and reset index
                                segments = new_segments
                                print("new_segments:", segments)
                                index = 0
                                ResetInterrupt()
                                break
                    if not is_path_correct:
                        is_path_correct = 1
                        break
                    
                    time.sleep(2)
                    current_location = cell
                    UpdateCurrentLocation(current_location)
                else:
                    index += 1
                break

            elif path_clearance == '2':
                print("Pausing...")
                continue

            else:
                # Recalculate the path from the last node printed considering new obstacles
                try:
                    new_path, obstacles = RecalculatePath(path_clearance, current_location, goal)
                    if not new_path:
                        print("No valid path found after recalculation.")
                        return
                    else:
                        print("New path:", new_path)
                        
                        # Break the new path into segments
                        new_segments = CreateSegments(new_path)
                        
                        # Plot the grid with new path and obstacles
                        ax.clear()  # Clear the previous plot
                        PlotGrid(ax, grid_size, current_location, goal, new_path, obstacles)
                        ax.figure.canvas.draw()  # Redraw the canvas
                        plt.pause(0.001)

                        # Update segments and reset index
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
    threading.Thread(target=lambda: app.run(port=5001)).start()

    ConnectMQTT()

    AGV_ID = int(input("Enter AGV ID: "))
    # Read the grid from the Excel file
    file_path = 'Floor Plan Sketcher\grid.xlsx' 
    grid_size = int(input("Enter the grid size (default is 32): ") or 32)
    fixed_grid = ReadGrid(file_path)

    # Create a copy of the fixed grid
    grid = copy.deepcopy(fixed_grid)

    # User input for start and end coordinates
    current_location = tuple(map(int, input("Enter start coordinates( Ex: For (1,18) type 1,18 ): ").strip().split(',')))

    while True:
        
        goal = ObtainGoal(AGV_ID)

        # Compute the path using D* Lite
        path = CalculatePath(current_location, goal, grid)
        print("Path:", path)

        # Initialize the plot
        fig, ax = plt.subplots(figsize=(10, 10))

        plt.ion()  # Turn on interactive mode

        # Plot the initial grid with the first path
        PlotGrid(ax, grid_size, current_location, goal, path)
        plt.pause(0.001)

        # Show the initial plot
        plt.show(block=False)

        # Break the path into straight-line segments
        segments = CreateSegments(path)
        print("segments:", segments)

        # Display the path interactively
        current_location = InteractivePathDisplay(segments, current_location, goal, ax)

        # Close the plot
        plt.close(fig)
