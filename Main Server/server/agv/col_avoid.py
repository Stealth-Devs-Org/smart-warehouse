import json

from flask import Blueprint, request

from server.agv.db_operations import save_agv_location
from server.agv.utils import (
    get_buffered_positions,
    get_close_agv_pairs,
    get_common_elements,
)

agv = Blueprint("agv", __name__)

agvs_data = {}


# This function returns the current locations of the AGVs as an array of cordinates.
def get_agv_locations_array(agvs_data):
    values = []
    for agv_id, data in agvs_data.items():
        if "location" in data:
            values.append(data["location"])
    return values


# This function returns the current obstacles in a segment of the path as an array of cordinates.
def find_obstacles_in_segment(segment):
    obstacles = get_common_elements(
        get_buffered_positions(1, get_agv_locations_array(agvs_data)), segment
    )
    return obstacles


from server.mqtt.utils import mqtt_client


# This function sends a stop signal to the AGV with the given ID. The AGV stalls for a while and then continues its path.
def stop_agv(agv_id):
    topic = f"{agv_id}/stop"
    message_dict = {"agv_id": agv_id, "action": "stop"}
    message_json = json.dumps(message_dict)
    mqtt_client.publish(topic, message_json)


# This function sends a recalibrate signal to the AGV with the given ID. The AGV stops and recalibrates its path and move.
def recalibrate_path(agv_id, segment):
    topic = f"{agv_id}/recalibrate"
    obstacles = find_obstacles_in_segment(segment)
    message_dict = {
        "agv_id": agv_id,
        "action": "recalibrate",
        "obstacles": obstacles,
    }
    mqtt_client.publish(topic, obstacles)


# This function checks for close AGV pairs and sends stop or recalibrate signals to the AGVs. This will be called on every update of AGV locations.
def collision_avoidance(agvs_data):
    close_agv_pairs = get_close_agv_pairs(agvs_data, 2)
    if close_agv_pairs:
        for agv_pair in close_agv_pairs:
            print(f"AGV pair: {agv_pair}")
            if agvs_data[agv_pair[0]]["status"] == 1 and agvs_data[agv_pair[1]]["status"] == 1:
                stop_agv(agv_pair[0])
                recalibrate_path(agv_pair[1], agvs_data[agv_pair[0]]["segment"])
            elif agvs_data[agv_pair[0]]["status"] == 1:
                recalibrate_path(agv_pair[0], agvs_data[agv_pair[1]]["segment"])
            elif agvs_data[agv_pair[1]]["status"] == 1:
                recalibrate_path(agv_pair[1], agvs_data[agv_pair[0]]["segment"])
            else:
                pass


def update_agv_location(data):
    agvs_data[data["agv_id"]] = data
    collision_avoidance(agvs_data)
    save_agv_location(data)


# def remove_agv_location(agv_id):
#     if agv_id in agv_locations:
#         del agv_locations[agv_id]


@agv.route("/path_clearance")
def path_clearance():
    data = request.json
    segment = data.get("segment")
    obstacles = find_obstacles_in_segment(segment)

    if not obstacles:
        return 1

    return obstacles
