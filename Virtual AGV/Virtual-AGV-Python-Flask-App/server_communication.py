import requests

MAIN_SERVER_URL = "http://127.0.0.1:5000"
# MAIN_SERVER_URL = "http://host.docker.internal:5000"


def RequestPathClearance(AGV_ID, segment):
    url = MAIN_SERVER_URL + "/path_clearance"
    payload = {"agv_id": f"agv{AGV_ID}", "segment": [segment[0], segment[-1]]}

    print(f"Requesting path clearance from {segment[0]} to {segment[-1]}...")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining path clearance: {e}")
        return None


def RequestPathClearance(AGV_ID, segment):
    url = MAIN_SERVER_URL + "/path_clearance"
    payload = {"agv_id": f"agv{AGV_ID}", "segment": [segment[0], segment[-1]]}

    print(f"Requesting path clearance from {segment[0]} to {segment[-1]}...")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("result")
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining path clearance: {e}")
        return None
