import time

from mqtt_handler import EndTask, UpdateCurrentLocation


status = 0

def SetStatus(new_status):
    global status
    status = new_status
    

def GetStatus():
    global status
    return status

def CreateSegments(path):
    segments = []
    if not path:
        return segments

    # if len(path) == 1:
    #     return [[path[0]]]

    current_segment = [path[0]]
    direction = None
    for i in range(1, len(path)):
        if path[i][0] == current_segment[-1][0]:
            new_direction = "vertical"
            if direction != new_direction:
                if direction:
                    segments.append(current_segment[0:-1])
                    current_segment = [current_segment[-1]]
                direction = new_direction
            current_segment.append(path[i])
        elif path[i][1] == current_segment[-1][1]:
            new_direction = "horizontal"
            if direction != new_direction:
                if direction:
                    segments.append(current_segment[0:-1])
                    current_segment = [current_segment[-1]]
                direction = new_direction
            current_segment.append(path[i])
    segments.append(current_segment)
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
    if action == 0:
        print("Stopped at ideal location")
        SetStatus(action)
        return direction
    elif action == 2 or action == 3:
        direction = SimulateTurning(
            AGV_ID, current_location, (storage[0], storage[1]), direction, turning_time
        )
        duration = LoadUnload(storage[2])
        SetStatus(action)
        if action == 2:
            print(f"AGV {AGV_ID} started loading at {current_location}...")
        else:
            print(f"AGV {AGV_ID} started unloading at {current_location}...")
        time.sleep(duration)
    elif action == 4:
        print(f"AGV {AGV_ID} started charging at {current_location}...")
        duration = 10
        SetStatus(action)
    UpdateCurrentLocation([current_location], AGV_ID, GetStatus())
    time.sleep(duration)
    SetStatus(0)
    EndTask(AGV_ID)
    UpdateCurrentLocation([current_location], AGV_ID, GetStatus())
    return direction


def SimulateTurning(AGV_ID, current_location, next_location, current_direction, turning_time):

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
    
    if (current_direction ==  direction):
        print("same direction:" + direction)
        return direction
    elif (
        (current_direction == "N" and direction == "E") or
        (current_direction == "E" and direction == "S") or
        (current_direction == "S" and direction == "W") or
        (current_direction == "W" and direction == "N")
    ):
        SetStatus(5) # Turning Right
    elif (
        (current_direction == "N" and direction == "W") or
        (current_direction == "W" and direction == "S") or
        (current_direction == "S" and direction == "E") or
        (current_direction == "E" and direction == "N")
    ):
        SetStatus(6) # Turning Left
    elif (
        (current_direction == "N" and direction == "S")
        or (current_direction == "S" and direction == "N")
        or (current_direction == "E" and direction == "W")
        or (current_direction == "W" and direction == "E")
    ):
        turning_time *= 2
        SetStatus(7) # Turning Back
    print("Turning from "+current_direction+" to "+direction)
    UpdateCurrentLocation([current_location], AGV_ID, GetStatus())
    time.sleep(turning_time)
    SetStatus(8) # Turning Completed
    UpdateCurrentLocation([current_location], AGV_ID, GetStatus())
    return direction


def EvalNewPath(new_segments, obstacles, remain_path, cell_time, turning_time):
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

    print("time to remain_path", time_to_remain_path)
    print("time to new_path", time_to_new_path)

    # Compare the times to decide whether the new path is better
    is_new_path_efficient = time_to_remain_path > time_to_new_path
    waiting_time = 0 if is_new_path_efficient else farthest_obstacle_distance * cell_time
    return is_new_path_efficient, waiting_time
