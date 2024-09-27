import math


def get_common_elements(array1, array2):
    set1 = set(tuple(x) for x in array1)
    set2 = set(tuple(x) for x in array2)

    common_elements = set1.intersection(set2)

    return [list(x) for x in common_elements]


"""
This function returns a list of positions that are within a buffer distance from the current agv positions.
The buffer distance is defined by the parameter buffer which is in units of blocks in warehouse.
This is done to avoid collisions with other agvs.
"""


def get_buffered_positions(buffer, current_agv_postions):
    buffered_positions = []
    for position in current_agv_postions:
        for i in range(-buffer, buffer + 1):
            for j in range(-buffer, buffer + 1):
                new_position = [position[0] + i, position[1] + j]
                if new_position not in buffered_positions:
                    buffered_positions.append(new_position)

    return buffered_positions


def calculate_distance(coord1, coord2):
    """
    Calculate the Euclidean distance between two coordinates.

    Parameters:
    coord1 (list): The first coordinate as [x1, y1].
    coord2 (list): The second coordinate as [x2, y2].

    Returns:
    float: The Euclidean distance between the two coordinates.
    """
    x1, y1 = coord1
    x2, y2 = coord2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def calculate_agv_distances(agvs_data):
    """
    Calculate the distances between AGVs based on their IDs and coordinates.

    Parameters:
    agv_locations (dict): A dictionary where keys are AGV IDs and values are coordinates [x1, y1].

    Returns:
    dict: A dictionary where the keys are tuples of AGV IDs and the values are the distances.
    """
    distances = {}
    agv_ids = list(agvs_data.keys())
    for i in range(len(agv_ids)):
        for j in range(i + 1, len(agv_ids)):
            agv_id1 = agv_ids[i]
            agv_id2 = agv_ids[j]
            coord1 = agvs_data[agv_id1]["location"]
            coord2 = agvs_data[agv_id2]["location"]
            distance = calculate_distance(coord1, coord2)
            distances[(agv_id1, agv_id2)] = distance

    # for agv_pair, distance in distances.items():
    #     print(f"Distance between {agv_pair[0]} and {agv_pair[1]}: {distance}")

    return distances


def get_close_agv_pairs(agvs_data, threshold):
    """
    Get AGV pairs that are closer than a threshold distance.

    Parameters:
    agv_locations (dict): A dictionary where keys are AGV IDs and values are coordinates (x, y).
    threshold (float): The threshold distance.

    Returns:
    list: A list of tuples representing AGV pairs that are closer than the threshold distance.
    """
    distances = calculate_agv_distances(agvs_data)
    close_pairs = [agv_pair for agv_pair, distance in distances.items() if distance < threshold]

    return close_pairs


def get_agvs_location_within_range(agvs_data, agv_id, threshold):
    """
    Get AGVs that are within a threshold distance from the given AGV.

    Parameters:
    agv_locations (dict): A dictionary where keys are AGV IDs and values are coordinates (x, y).
    agv_id (str): The ID of the AGV.
    threshold (float): The threshold distance.

    Returns:
    list: A list of AGV IDs that are within the threshold distance from the given AGV.
    """
    distances = calculate_agv_distances(agvs_data)
    agvs_within_range = []
    for (agv_id1, agv_id2), distance in distances.items():
        if (agv_id1 == agv_id or agv_id2 == agv_id) and distance <= threshold:
            if agv_id1 != agv_id:
                agvs_within_range.append(agvs_data[agv_id1]["location"])
            if agv_id2 != agv_id:
                agvs_within_range.append(agvs_data[agv_id2]["location"])

    return agvs_within_range


def get_distance_of_furthest_obstacle(agv_location, obstacles):
    """
    Get the distance of the furthest obstacle from the AGV location.

    Parameters:
    agv_location (list): The current location of the AGV as [x, y].
    obstacles (list): A list of obstacle locations as [x, y].

    Returns:
    float: The distance of the furthest obstacle from the AGV location.
    """
    max_distance = 0
    for obstacle in obstacles:
        distance = calculate_distance(agv_location, obstacle)
        if distance > max_distance:
            max_distance = distance

    return max_distance


def is_segment_occupied(agvs_data, agv_id, segment):
    """
    Check if the segment of the path is occupied by other AGVs.

    Parameters:
    agvs_data (dict): A dictionary containing AGV data.
    agv_id (str): The ID of the AGV.
    segment (list): A list of coordinates representing the segment of the path.

    Returns:
    bool: True if the segment is occupied, False otherwise.
    """
    for agv in agvs_data.values():
        if (
            "location" in agv
            and agv["agv_id"] != agv_id
            and (agv["segment"] in segment or segment in agv["segment"])
        ):
            return True


def is_path_crossing(agv_1, agv_2):
    """
    Check if the paths of two AGVs are crossing.

    Parameters:
    agv_1 (dict): The data of the first AGV.
    agv_2 (dict): The data of the second AGV.

    Returns:
    bool: True if the paths are crossing, False otherwise.
    """
    loc_1 = agv_1["location"]
    loc_2 = agv_2["location"]
    path_1 = agv_1["segment"]
    path_2 = agv_2["segment"]

    if loc_1 in path_2 or loc_2 in path_1:
        return True
    else:
        for i in range(len(path_1)):
            if path_1[i] in path_2:
                return True
        for i in range(len(path_2)):
            if path_2[i] in path_1:
                return True

    return False
