import json
import threading
import time

from flask import Blueprint, jsonify, render_template, request

from server.agv.db_operations import save_agv_location
from server.agv.utils import (
    get_agvs_location_within_range,
    get_buffered_positions,
    get_close_agv_pairs,
    get_common_elements,
    get_distance_of_furthest_obstacle,
    is_path_crossing,
    is_segment_occupied,
)

agv = Blueprint("agv", __name__)

agvs_data = {}

sent_interrupts = {}

timeout_segments = {}


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
def stop_agv(agv_id):
    if agv_id in sent_interrupts and sent_interrupts[agv_id]["interrupt"] == 1:
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


# This function sends a recalibrate signal to the AGV with the given ID. The AGV stops and recalibrates its path and move.
def recalibrate_path(agv_id, segment):
    topic = f"{agv_id}/interrupt"
    # obstacles = find_obstacles_in_segment(agvs_data, agv_id, segment)
    obstacles = []
    if agv_id in sent_interrupts and sent_interrupts[agv_id]["interrupt"] == obstacles:
        return
    message_dict = {"interrupt": obstacles}
    message_json = json.dumps(message_dict)
    mqtt_client.publish(topic, message_json, qos=2)
    print(f"Sent recalibrate signal to AGV {agv_id}")

    if agv_id not in sent_interrupts:
        sent_interrupts[agv_id] = {}
    sent_interrupts[agv_id]["interrupt"] = obstacles
    sent_interrupts[agv_id]["location"] = agvs_data[agv_id]["location"]


# This function checks for close AGV pairs and sends stop or recalibrate signals to the AGVs. This will be called on every update of AGV locations.
def collision_avoidance():
    close_agv_pairs = get_close_agv_pairs(agvs_data, 2.5)
    if close_agv_pairs:
        for agv_pair in close_agv_pairs:
            if is_path_crossing(agvs_data[agv_pair[0]], agvs_data[agv_pair[1]]):
                print(f"Path crossing detected between AGV {agv_pair[0]} and AGV {agv_pair[1]}")
                if agvs_data[agv_pair[0]]["status"] == 1 and agvs_data[agv_pair[1]]["status"] == 1:
                    stop_agv(agv_pair[0])
                    recalibrate_path(agv_pair[1], agvs_data[agv_pair[1]]["segment"])
                elif agvs_data[agv_pair[0]]["status"] == 1:
                    stop_agv(agv_pair[1])
                    recalibrate_path(agv_pair[0], agvs_data[agv_pair[0]]["segment"])
                elif agvs_data[agv_pair[1]]["status"] == 1:
                    stop_agv(agv_pair[0])
                    recalibrate_path(agv_pair[1], agvs_data[agv_pair[1]]["segment"])
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
    agvs_data[data["agv_id"]] = data
    socketio.emit("agv_location", agvs_data)
    # print(agvs_data)
    collision_avoidance()

    # Remove the interrupt if the AGV has moved from the location
    if (
        data["agv_id"] in sent_interrupts.keys()
        and sent_interrupts[data["agv_id"]]["location"] != data["location"]
    ):
        del sent_interrupts[data["agv_id"]]

    # Remove the AGV location from permanent obstacles if it is back alive
    remove_from_permanent_obstacles(data["agv_id"])

    save_agv_location(data)


# def remove_agv_location(agv_id):
#     if agv_id in agv_locations:
#         del agv_locations[agv_id]


def timeout_segment_manager():
    global timeout_segments
    while True:
        for segment in list(timeout_segments):
            if time.time() - timeout_segments[segment] > 1:
                del timeout_segments[segment]
        time.sleep(1)


def start_timeout_segment_manager():
    thread = threading.Thread(target=timeout_segment_manager)
    thread.daemon = True
    thread.start()


start_timeout_segment_manager()


@agv.route("/path_clearance", methods=["POST"])
def path_clearance():
    data = request.json
    agv_id = data["agv_id"]
    segment = data["segment"]
    segment_tuple = tuple(tuple(inner) for inner in segment)

    if segment_tuple in timeout_segments:
        obstacles = [segment[0]]
    else:
        obstacles = find_obstacles_in_segment(agvs_data, agv_id, segment)

    if not obstacles:
        agvs_data[agv_id]["segment"] = segment
        timeout_segments[segment_tuple] = time.time()
        message_dict = {"result": 1}
        message_json = json.dumps(message_dict)
        return message_json
    else:
        message_dict = {"result": obstacles}
        message_json = json.dumps(message_dict)
        return message_json


@agv.route("/")
def index():
    return render_template("grid.html")


@agv.route("/get_dynamic_locations")
def get_dynamic_locations():
    # agv_locations = get_agv_locations_array(agvs_data)
    # Return the dynamic dot color data
    return jsonify(agvs_data)
