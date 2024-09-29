import json
import threading
import time

from flask import Blueprint, jsonify, render_template, request

from server.agv.db_operations import save_agv_location
from server.agv.utils import (
    Get_values_from_agv_json,
    Get_values_from_sent_interrupt_json,
    Update_agv_json,
    Update_sent_interrupt_json,
    get_agvs_location_within_range,
    get_buffered_positions,
    get_close_agv_pairs,
    get_common_elements,
    get_distance_of_furthest_obstacle,
    is_path_crossing,
    is_segment_occupied,
)

agv = Blueprint("agv", __name__)


# timeout_segments = {}


# This function returns the current locations of the AGVs as an array of cordinates.
def get_agv_locations_array(agvs_data):
    values = []
    for agv_id, data in agvs_data.items():
        if "location" in data:
            values.append(data["location"])
    return values


from server.agv.keep_alive import permanent_obstacles, remove_from_permanent_obstacles


# This function returns the current obstacles in a segment of the path as an array of cordinates.
def find_obstacles_in_segment(agvs_data, agv_id, segment):
    obstacles = get_common_elements(get_agv_locations_array(agvs_data), segment)

    # Add permanent obstacles to the list
    if permanent_obstacles:
        obstacles = obstacles + get_common_elements(permanent_obstacles.values(), segment)

    cur_agv_loc = agvs_data[agv_id]["location"]
    if cur_agv_loc in obstacles:
        obstacles = [obstacle for obstacle in obstacles if obstacle != cur_agv_loc]

    # obstacles = get_buffered_positions(1, obstacles) # No need to buffer the obstacles

    if obstacles:
        furthest_obstacle_distance = get_distance_of_furthest_obstacle(cur_agv_loc, obstacles)
        obstacles_within_range = get_agvs_location_within_range(
            agvs_data, agv_id, furthest_obstacle_distance
        )
        obstacles = obstacles + obstacles_within_range
        obstacles = list(set(tuple(obstacle) for obstacle in obstacles))

    return obstacles


from server.mqtt.utils import mqtt_client


# This function sends a stop signal to the AGV with the given ID. The AGV stalls for a while and then continues its path.
def stop_agv(agv_id, col_agv_id):
    sent_interrupts = Get_values_from_sent_interrupt_json()
    agvs_data = Get_values_from_agv_json()
    if (
        agv_id in sent_interrupts and col_agv_id == sent_interrupts[agv_id]["col_agv_id"]
    ) and sent_interrupts[agv_id]["interrupt"] == 1:
        return
    topic = f"{agv_id}/interrupt"
    message_dict = {"interrupt": 1}
    message_json = json.dumps(message_dict)
    mqtt_client.publish(topic, message_json, qos=2)
    print(f"Sent stop signal to AGV {agv_id}")

    if agv_id not in sent_interrupts:
        sent_interrupts[agv_id] = {}
    sent_interrupts[agv_id]["interrupt"] = 1
    sent_interrupts[agv_id]["location"] = agvs_data[agv_id]["location"]
    sent_interrupts[agv_id]["col_agv_id"] = col_agv_id
    Update_sent_interrupt_json(sent_interrupts)


# This function sends a recalibrate signal to the AGV with the given ID. The AGV stops and recalibrates its path and move.
def recalibrate_path(agv_id, segment, crossing_segment, col_agv_id):
    topic = f"{agv_id}/interrupt"
    # obstacles = find_obstacles_in_segment(agvs_data, agv_id, segment)
    obstacles = []
    # obstacles = obstacles + crossing_segment
    # if obstacles:
    #     obstacles = list(set(tuple(obstacle) for obstacle in obstacles))
    sent_interrupts = Get_values_from_sent_interrupt_json()
    agvs_data = Get_values_from_agv_json()
    if (agv_id in sent_interrupts and col_agv_id == sent_interrupts[agv_id]["col_agv_id"]) and (
        sent_interrupts[agv_id]["interrupt"] == 1
        or sent_interrupts[agv_id]["interrupt"] == obstacles
    ):
        return
    message_dict = {"interrupt": obstacles}
    message_json = json.dumps(message_dict)
    mqtt_client.publish(topic, message_json, qos=2)
    print(f"Sent recalibrate signal to AGV {agv_id}")

    if agv_id not in sent_interrupts:
        sent_interrupts[agv_id] = {}
    sent_interrupts[agv_id]["interrupt"] = obstacles
    sent_interrupts[agv_id]["location"] = agvs_data[agv_id]["location"]
    sent_interrupts[agv_id]["col_agv_id"] = col_agv_id
    Update_sent_interrupt_json(sent_interrupts)


# This function checks for close AGV pairs and sends stop or recalibrate signals to the AGVs. This will be called on every update of AGV locations.
def collision_avoidance():
    agvs_data = Get_values_from_agv_json()
    close_agv_pairs = get_close_agv_pairs(agvs_data, 2)
    if close_agv_pairs:
        for agv_pair in close_agv_pairs:
            crossing_segment = is_path_crossing(agvs_data[agv_pair[0]], agvs_data[agv_pair[1]])
            if crossing_segment != []:
                print(f"Path crossing detected between AGV {agv_pair[0]} and AGV {agv_pair[1]}")
                if agvs_data[agv_pair[0]]["status"] == 1 and agvs_data[agv_pair[1]]["status"] == 1:
                    stop_agv(agv_pair[0], agv_pair[1])
                    recalibrate_path(
                        agv_pair[1],
                        agvs_data[agv_pair[1]]["segment"],
                        crossing_segment,
                        agv_pair[0],
                    )
                elif agvs_data[agv_pair[0]]["status"] == 1:
                    recalibrate_path(
                        agv_pair[0],
                        agvs_data[agv_pair[0]]["segment"],
                        crossing_segment,
                        agv_pair[1],
                    )
                elif agvs_data[agv_pair[1]]["status"] == 1:
                    recalibrate_path(
                        agv_pair[1],
                        agvs_data[agv_pair[1]]["segment"],
                        crossing_segment,
                        agv_pair[0],
                    )
                else:
                    pass


def run_collision_avoidance(interval):
    def start():
        print("Collision monitoring started")
        while True:
            collision_avoidance()
            time.sleep(interval)

    thread = threading.Thread(target=start)
    thread.start()


from server.websocket.utils import socketio


def update_agv_location(data):
    temp_agvs_data = {}
    temp_agvs_data[data["agv_id"]] = data
    Update_agv_json(temp_agvs_data)
    all_agvs_data = Get_values_from_agv_json()
    socketio.emit("agv_location", all_agvs_data)
    # print(agvs_data)
    collision_avoidance()

    # Remove the interrupt if the AGV has moved from the location
    sent_interrupts = Get_values_from_sent_interrupt_json()
    if (
        data["agv_id"] in sent_interrupts.keys()
        and sent_interrupts[data["agv_id"]]["location"] != data["location"]
    ):
        sent_interrupts[data["agv_id"]] = None
        Update_sent_interrupt_json(sent_interrupts)

    # Remove the AGV location from permanent obstacles if it is back alive
    remove_from_permanent_obstacles(data["agv_id"])

    save_agv_location(data)


# def remove_agv_location(agv_id):
#     if agv_id in agv_locations:
#         del agv_locations[agv_id]


# def timeout_segment_manager():
#     global timeout_segments
#     while True:
#         for segment in list(timeout_segments):
#             if time.time() - timeout_segments[segment] > 1:
#                 del timeout_segments[segment]
#         time.sleep(1)


# def start_timeout_segment_manager():
#     thread = threading.Thread(target=timeout_segment_manager)
#     thread.daemon = True
#     thread.start()


# start_timeout_segment_manager()


@agv.route("/path_clearance", methods=["POST"])
def path_clearance():
    data = request.json
    agv_id = data["agv_id"]
    segment = data["segment"]

    agvs_data = Get_values_from_agv_json()
    if agv_id in agvs_data:
        agvs_data[agv_id]["segment"] = segment
        agvs_data[agv_id]["status"] = 1
        Update_agv_json(agvs_data)
        time.sleep(1)
        obstacles = find_obstacles_in_segment(agvs_data, agv_id, segment)
        if not obstacles:
            # timeout_segments[segment_tuple] = time.time()
            message_dict = {"result": 1}
            message_json = json.dumps(message_dict)
            return message_json
        else:
            agvs_data[agv_id]["segment"] = [agvs_data[agv_id]["location"]]
            Update_agv_json(agvs_data)
            message_dict = {"result": obstacles}
            message_json = json.dumps(message_dict)
            return message_json
    else:
        print(f"AGV with id {agv_id} not found")
        message_dict = {"result": None}
        message_json = json.dumps(message_dict)
        return message_json


@agv.route("/")
def index():
    return render_template("grid.html")


@agv.route("/get_dynamic_locations")
def get_dynamic_locations():
    agvs_data = Get_values_from_agv_json()
    # agv_locations = get_agv_locations_array(agvs_data)
    # Return the dynamic dot color data
    return jsonify(agvs_data)


@agv.route("/get_permanent_obstacles")
def get_permanent_obstacles():
    return jsonify(permanent_obstacles)
