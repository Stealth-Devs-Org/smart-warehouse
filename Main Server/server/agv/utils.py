import math


def get_common_elements(array1, array2):
    set1 = set(array1)
    set2 = set(array2)

    common_elements = set1.intersection(set2)

    return list(common_elements)


"""
This function returns a list of positions that are within a buffer distance from the current agv positions.
The buffer distance is defined by the parameter buffer which is in units of blocks in warehouse.
This is done to avoid collisions with other agvs.
"""


def get_buffered_positions(buffer, current_agv_postions):
    buffered_positions = current_agv_postions.copy()
    for position in current_agv_postions:
        for i in range(-buffer, buffer + 1):
            for j in range(-buffer, buffer + 1):
                buffered_positions.append([position[0] + i, position[1] + j])

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
