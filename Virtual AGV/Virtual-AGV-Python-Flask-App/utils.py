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

