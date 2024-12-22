import os
import time
import csv
import ujson as json

agv_state = {}


def CreateSegments(path):
    start_time = time.time()
    segments = []
    if not path:
        return segments

    current_segment = [path[0]]
    direction = None
    for i in range(1, len(path)):
        if path[i][0] == current_segment[-1][0]:
            new_direction = "vertical"
            if direction != new_direction:
                if direction:
                    segments.append(current_segment)
                    current_segment = [current_segment[-1]]
                direction = new_direction
            current_segment.append(path[i])
        elif path[i][1] == current_segment[-1][1]:
            new_direction = "horizontal"
            if direction != new_direction:
                if direction:
                    segments.append(current_segment)
                    current_segment = [current_segment[-1]]
                direction = new_direction
            current_segment.append(path[i])
    segments.append(current_segment)
    end_time = time.time()
    SaveProcessTime('segmentCreationTime.csv',start_time, end_time)
    return segments


def LoadUnload(storage_level):
    if storage_level == 1:
        return 1
    elif storage_level == 2:
        return 2
    elif storage_level == 3:
        return 3
    elif storage_level == 4:
        return 4
    else:
        return 5


def SimulateEndAction(AGV_ID, current_location, direction, storage, action, turning_time):
    # from app import agv_state
    from mqtt_handler import EndTask, UpdateCurrentLocation

    if action == 0:
        # ---------- print("Stopped at ideal location")
        return direction
    elif action == 2 or action == 3:
        direction = SimulateTurning(
            AGV_ID, current_location, (storage[0], storage[1]), direction, turning_time
        )
        duration = LoadUnload(storage[2])
        '''if action == 2:
            print(f"AGV {AGV_ID} started loading at {current_location}...")
        else:
            print(f"AGV {AGV_ID} started unloading at {current_location}...")'''
        time.sleep(duration)
    elif action == 4:
        # ---------- print(f"AGV {AGV_ID} started charging at {current_location}...")
        duration = 10
    agv_state["current_status"] = action
    agv_state["current_direction"] = direction
    UpdateCurrentLocation()
    time.sleep(duration)
    agv_state["current_status"] = 0
    EndTask(AGV_ID)
    UpdateCurrentLocation()
    return direction


def SimulateTurning(AGV_ID, current_location, next_location, current_direction, turning_time):
    # from app import agv_state
    from mqtt_handler import UpdateCurrentLocation

    if current_location[0] == next_location[0] and current_location[1] == next_location[1]:
        return current_direction
    elif current_location[0] == next_location[0] and current_location[1] < next_location[1]:
        direction = "N"
    elif current_location[0] == next_location[0] and current_location[1] > next_location[1]:
        direction = "S"
    elif current_location[0] < next_location[0] and current_location[1] == next_location[1]:
        direction = "E"
    else:
        direction = "W"

    if current_direction == direction:
        # ---------- print("same direction:" + direction)
        return direction
    elif (
        (current_direction == "N" and direction == "E")
        or (current_direction == "E" and direction == "S")
        or (current_direction == "S" and direction == "W")
        or (current_direction == "W" and direction == "N")
    ):
        agv_state["current_status"] = 5  # Turning Right
    elif (
        (current_direction == "N" and direction == "W")
        or (current_direction == "W" and direction == "S")
        or (current_direction == "S" and direction == "E")
        or (current_direction == "E" and direction == "N")
    ):
        agv_state["current_status"] = 6  # Turning Left
    elif (
        (current_direction == "N" and direction == "S")
        or (current_direction == "S" and direction == "N")
        or (current_direction == "E" and direction == "W")
        or (current_direction == "W" and direction == "E")
    ):
        turning_time *= 2
        agv_state["current_status"] = 7  # Turning Back
    print("Turning from " + current_direction + " to " + direction)
    UpdateCurrentLocation()
    time.sleep(turning_time)
    agv_state["current_status"] = 8  # Turning Completed
    UpdateCurrentLocation()
    return direction


def EvalNewPath(new_segments, obstacles, remain_path, cell_time, turning_time):
    start_time = time.time()
    # Find the farthest obstacle from the start of the remaining path
    start_point = remain_path[0][0]  # First point in the remaining path
    farthest_obstacle_distance = max(
        abs(obstacle[0] - start_point[0]) + abs(obstacle[1] - start_point[1])
        for obstacle in obstacles
    )

    # Calculate total time for remaining path and new path
    time_to_remain_path = (
        farthest_obstacle_distance + sum(len(segment) for segment in remain_path)
    ) * cell_time + len(remain_path) * turning_time
    time_to_new_path = (
        sum(len(segment) for segment in new_segments) * cell_time + len(new_segments) * turning_time
    )

    # ---------- print("time to remain_path", time_to_remain_path)
    # ---------- print("time to new_path", time_to_new_path)

    # Compare the times to decide whether the new path is better
    is_new_path_efficient = time_to_remain_path > time_to_new_path
    waiting_time = 0 if is_new_path_efficient else farthest_obstacle_distance * cell_time
    end_time = time.time()
    SaveProcessTime('pathEvaluationTime.csv',start_time, end_time)
    return is_new_path_efficient, waiting_time


import threading

# Create a file lock
file_lock = threading.Lock()


def SaveToCSV(agv_id, t1, t2, t3, t4, filename):
    # Check if file exists
    file_exists = os.path.isfile(filename)

    # Open CSV file in append mode
    with open(filename, mode="a", newline='') as file:
        writer = csv.writer(file)

        # If file does not exist, write the header
        if not file_exists:
            writer.writerow(["AGV_Id", "t1", "t2", "t3", "t4"])  # Write the header

        # Write the row with timestamps
        writer.writerow([agv_id, t1, t2, t3, t4])

def SaveProcessTime(filename, t1, t2, t3=0):
    # Check if file exists
    file_exists = os.path.isfile(filename)

    # Open CSV file in append mode
    with open(filename, mode="a", newline='') as file:
        writer = csv.writer(file)

        if t3!=0:
            # If file does not exist, write the header
            if not file_exists:
                writer.writerow(["t1", "t2", "t3"])  # Write the header

            # Write the row with timestamps
            writer.writerow([t1, t2, t3])
        else:
            # If file does not exist, write the header
            if not file_exists:
                writer.writerow(["t1", "t2"])  # Write the header

            # Write the row with timestamps
            writer.writerow([t1, t2])