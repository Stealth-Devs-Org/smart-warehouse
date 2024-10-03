import datetime
import json
import threading
import time

from flask import Blueprint, jsonify, render_template, request

from server.agv.db_operations import save_agv_location
from server.agv.utils import (
    Update_collisions_json,
    get_agvs_location_within_range,
    get_close_agv_pairs,
    get_common_elements,
    get_high_value_agv_id,
    is_path_crossing,
)
from server.websocket.websocket import (
    send_agv_data_through_websocket,
    send_through_websocket,
)

agv = Blueprint("agv", __name__)


agvs_data = {}
sent_interrupts = {}


# This function returns the current locations of the AGVs as an array of cordinates.
def get_agv_locations_array(agvs_data):
    values = []
    for agv_id, data in agvs_data.items():
        if "location" in data:
            values.append(data["location"])
    return values


from server.agv.keep_alive import remove_from_permanent_obstacles


# This function returns the current obstacles in a segment of the path as an array of cordinates.
def find_obstacles_in_segment(agvs_data, agv_id, segment):
    obstacles = get_common_elements(get_agv_locations_array(agvs_data), segment)

    # Add permanent obstacles to the list
    from server.agv.keep_alive import permanent_obstacles

    # permanent_obstacles = Get_values_from_permanent_obstacles_json()
    if permanent_obstacles:
        obstacles = obstacles + get_common_elements(permanent_obstacles.values(), segment)

    cur_agv_loc = agvs_data[agv_id]["location"]
    if cur_agv_loc in obstacles:
        obstacles = [obstacle for obstacle in obstacles if obstacle != cur_agv_loc]

    # obstacles = get_buffered_positions(1, obstacles) # No need to buffer the obstacles

    if obstacles:
        # furthest_obstacle_distance = get_distance_of_furthest_obstacle(cur_agv_loc, obstacles)
        range_of_obstacle_detection = 3
        obstacles_within_range = get_agvs_location_within_range(
            agvs_data, agv_id, range_of_obstacle_detection
        )
        obstacles = obstacles + obstacles_within_range
        obstacles = list(set(tuple(obstacle) for obstacle in obstacles))
        obstacles = list(set(tuple(obstacle) for obstacle in obstacles))

    return obstacles


from server.mqtt.utils import mqtt_client


# This function sends a stop signal to the AGV with the given ID. The AGV stalls for a while and then continues its path.
def stop_agv(agv_id, col_agv_id):

    if (agv_id in sent_interrupts) and sent_interrupts[agv_id]["interrupt"] == 1:
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


# This function sends a recalibrate signal to the AGV with the given ID. The AGV stops and recalibrates its path and move.
def recalibrate_path(agv_id, segment, col_agv_id, crossing_segment=[]):

    if agv_id in sent_interrupts and (
        col_agv_id == sent_interrupts[agv_id]["col_agv_id"]
        or sent_interrupts[agv_id]["interrupt"] == 1
    ):
        return

    topic = f"{agv_id}/interrupt"
    message_dict = {"interrupt": 2}
    message_json = json.dumps(message_dict)
    mqtt_client.publish(topic, message_json, qos=2)
    print(f"Sent recalibrate signal to AGV {agv_id}")

    if agv_id not in sent_interrupts:
        sent_interrupts[agv_id] = {}
    sent_interrupts[agv_id]["interrupt"] = 2
    sent_interrupts[agv_id]["location"] = agvs_data[agv_id]["location"]
    sent_interrupts[agv_id]["col_agv_id"] = col_agv_id


# This function checks for close AGV pairs and sends stop or recalibrate signals to the AGVs. This will be called on every update of AGV locations.
def collision_avoidance():

    close_agv_pairs = get_close_agv_pairs(agvs_data, 2)
    if close_agv_pairs:
        for agv_pair in close_agv_pairs:
            crossing_segment = is_path_crossing(agvs_data[agv_pair[0]], agvs_data[agv_pair[1]])
            if crossing_segment != []:
                print(
                    f"Path crossing detected between AGV {agv_pair[0]} and AGV {agv_pair[1]} crossing segment {crossing_segment}"
                )
                agv_pair = get_high_value_agv_id(agv_pair[0], agv_pair[1])
                stop_agv(agv_pair[0], agv_pair[1])
                recalibrate_path(
                    agv_pair[1],
                    agvs_data[agv_pair[1]]["segment"],
                    agv_pair[0],
                )
    detect_collision()


def run_collision_avoidance(interval):
    def start():
        print("Collision monitoring started")
        while True:
            collision_avoidance()
            time.sleep(interval)

    thread = threading.Thread(target=start)
    thread.daemon = True
    thread.start()


from server.websocket.utils import socketio


def detect_collision():
    for agv_id, data in agvs_data.items():
        for agv_id2, data2 in agvs_data.items():
            if agv_id != agv_id2:
                if data["location"] == data2["location"]:
                    print(
                        f"Collision detected between AGV {agv_id} and AGV {agv_id2} at {data['location']}"
                    )
                    temp = {}
                    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    temp["timestamp"] = timestamp
                    temp["agv1"] = agv_id
                    temp["agv2"] = agv_id2
                    temp["location"] = data["location"]
                    temp["agv1_path"] = data["segment"]
                    temp["agv2_path"] = data2["segment"]
                    temp["agv1_status"] = data["status"]
                    temp["agv2_status"] = data2["status"]
                    Update_collisions_json(temp)


def update_agv_location(data):
    agvs_data[data["agv_id"]] = data

    from server.agv.keep_alive import permanent_obstacles
    from server.websocket.utils import emit_to_webpage

    collision_avoidance()

    emit_to_webpage(agvs_data, permanent_obstacles)
    # send_through_websocket({"agvs_data": agvs_data})  # Send the AGV data to the Unity warehouse
    send_agv_data_through_websocket(data)  # Send the AGV data to the web page

    # Remove the AGV location from permanent obstacles since it is back alive
    remove_from_permanent_obstacles(data["agv_id"])

    save_agv_location(data)


@agv.route("/path_clearance", methods=["POST"])
def path_clearance():
    data = request.json
    agv_id = data["agv_id"]
    segment = data["segment"]

    if agv_id in agvs_data.keys():

        if (
            agv_id in sent_interrupts.keys()
            and sent_interrupts[agv_id]["interrupt"] == 2
            and sent_interrupts[agv_id]["col_agv_id"] not in sent_interrupts.keys()
        ):
            del sent_interrupts[agv_id]
        elif data["agv_id"] in sent_interrupts.keys() and sent_interrupts[agv_id]["interrupt"] == 1:
            del sent_interrupts[agv_id]
        collision_avoidance()

        obstacles = find_obstacles_in_segment(agvs_data, agv_id, segment)
        if not obstacles:
            agvs_data[agv_id]["segment"] = segment
            message_dict = {"result": 1}
            message_json = json.dumps(message_dict)
            return message_json
        else:
            agvs_data[agv_id]["segment"] = [agvs_data[agv_id]["location"]]
            message_dict = {"result": obstacles}
            message_json = json.dumps(message_dict)
            return message_json
    else:
        print(f"AGV with id {agv_id} not found")
        print(agvs_data.keys())
        message_dict = {"result": 0}  # 0 means AGV not found
        message_json = json.dumps(message_dict)
        return message_json


@agv.route("/")
def index():
    return render_template("grid.html")


@agv.route("/get_goal", methods=["POST"])
def get_goal():
    from server.agv.scheduler import generate_random_task, task_divider, working_agvs

    data = request.json
    agv_id = data["agv_id"]
    if agv_id in working_agvs.keys():
        task = working_agvs[agv_id]
        sending_task = task_divider(task)
    else:
        task = generate_random_task()
        task["assigned_agv"] = agv_id
        working_agvs[agv_id] = task
        task = working_agvs[agv_id]
        sending_task = task_divider(task)
    message_json = json.dumps(sending_task)
    return message_json


@agv.route("/get_dynamic_locations")
def get_dynamic_locations():
    # Return the dynamic dot color data
    return jsonify(agvs_data)


@agv.route("/get_permanent_obstacles")
def get_permanent_obstacles():
    from server.agv.keep_alive import permanent_obstacles

    return jsonify(permanent_obstacles)
