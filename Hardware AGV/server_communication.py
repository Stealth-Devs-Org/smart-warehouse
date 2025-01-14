import time

import requests

from utils import SaveToCSV

MAIN_SERVER_URL = "http://192.168.110.144:5000"
# MAIN_SERVER_URL = "http://host.docker.internal:5000"


def RequestPathClearance(AGV_ID, segment):
    url = MAIN_SERVER_URL + "/path_clearance"
    payload = {
        "agv_id": f"agv{AGV_ID}",
        "segment": segment,
        "result": 0,  # Dummy value in the format of response from server
    }
    # Capture t1 (time when the request is sent)
    t1 = time.time()
    payload["t1"] = t1  # Add t1 to the payload
    payload["t2"] = t1  # Dummy values in the format of response from server
    payload["t3"] = t1  # Dummy values in the format of response from server

    print(f"Requesting path clearance for segment: {segment}")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        # Capture t4 (time when the response is received)
        t4 = time.time()

        response_data = response.json()

        # Read t1, t2, t3 from server response
        t1_server = response_data.get("t1")
        t2 = response_data.get("t2")
        t3 = response_data.get("t3")

        # Save t1, t2, t3, t4 to a CSV file
        SaveToCSV("agv" + str(AGV_ID), t1_server, t2, t3, t4, "get_path_clearance.csv")
        return response_data.get("result")
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining path clearance: {e}")
        return None


def ObtainGoalHttp(AGV_ID):
    url = MAIN_SERVER_URL + "/get_goal"
    payload = {
        "agv_id": f"agv{AGV_ID}",
        "destination": (0, 0),  # Dummy values in the format of response from server
        "storage": (0, 0, 0),  # Dummy values in the format of response from server
        "action": 2,  # Dummy values in the format of response from server
    }
    # Capture t1 (time when the request is sent)
    t1 = time.time()
    payload["t1"] = t1  # Add t1 to the payload
    payload["t2"] = t1  # Dummy values in the format of response from server
    payload["t3"] = t1  # Dummy values in the format of response from server

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        # Capture t4 (time when the response is received)
        t4 = time.time()

        response_data = response.json()

        # Read t1, t2, t3 from server response
        t1_server = response_data.get("t1")
        t2 = response_data.get("t2")
        t3 = response_data.get("t3")

        # Save t1, t2, t3, t4 to a CSV file
        SaveToCSV("agv" + str(AGV_ID), t1_server, t2, t3, t4, "get_goal.csv")

        return response_data
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining goal: {e}")
        return None
