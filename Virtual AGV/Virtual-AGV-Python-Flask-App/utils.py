import time

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

def SimulateLoadingUnloading(current_location):
    print(f"Loading and unloading at location: {current_location}")
    time.sleep(2)  # Simulate loading and unloading time

def SimulateTurning(current_location, next_location, current_direction, turning_time):
    
    if current_location[0] == next_location[0] and current_location[1] < next_location[1]:
        direction = "N"
    elif current_location[0] == next_location[0] and current_location[1] > next_location[1]:
        direction = "S"
    elif current_location[0] < next_location[0] and current_location[1] == next_location[1]:
        direction = "E"
    else:
        direction = "W"

    print(f"Turning from {current_direction} to {direction}...")
    print(time.time())
    if current_direction == "N" and (direction == "E" or direction == "W"):
        time.sleep(turning_time)
        print(time.time())
    elif current_direction == "S" and (direction == "E" or direction == "W"):
        time.sleep(turning_time)
        print(time.time())
    elif current_direction == "E" and (direction == "N" or direction == "S"):
        time.sleep(turning_time)
        print(time.time())
    elif current_direction == "W" and (direction == "N" or direction == "S"):
        time.sleep(turning_time)
        print(time.time())
    elif (current_direction == "N" and direction == "S") or (current_direction == "S" and direction == "N") or (current_direction == "E" and direction == "W") or (current_direction == "W" and direction == "E"):
        time.sleep(turning_time*2)
        print(time.time())

    return direction