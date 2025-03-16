import requests
import time
from utils import SaveCommunicationTime, SavePacketData
MAIN_SERVER_URL = "http://127.0.0.1:5000"
# MAIN_SERVER_URL = "http://host.docker.internal:5000"
goal_request_id = 0
path_clearance_request_id = 0

def RequestPathClearance(AGV_ID, segment):
    url = MAIN_SERVER_URL + "/path_clearance"
    packet_type = 3
    global path_clearance_request_id
    path_clearance_request_id += 1
    sent_packet_id = f"agv{AGV_ID}/{packet_type}/{path_clearance_request_id}" 
    payload = {"id": sent_packet_id,
               "agv_id": f"agv{AGV_ID}", 
               "segment": segment,
               "result": 0, # Dummy value in the format of response from server
               }
    # Capture t1 (time when the request is sent)
    t1 = time.time()
    payload["t1"] = t1  # Add t1 to the payload
    payload["t2"] = t1 # Dummy values in the format of response from server
    payload["t3"] = t1 # Dummy values in the format of response from server

    # ---------- print(f"Requesting path clearance for segment: {segment}")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        # Capture t4 (time when the response is received)
        t4 = time.time()

        response_data = response.json()

        recieve_packet_id = response_data.get("id")

        # Read t1, t2, t3 from server response
        t1_server = response_data.get("t1")
        t2 = response_data.get("t2")
        t3 = response_data.get("t3")

        # Save t1, t2, t3, t4 to a CSV file
        SaveCommunicationTime("agv"+str(AGV_ID), t1_server, t2, t3, t4, "get_path_clearance.csv")
        SavePacketData(sent_packet_id, "agv"+str(AGV_ID), "path_clearance_request", "sent_packets.csv")
        SavePacketData(recieve_packet_id, "agv"+str(AGV_ID), "path_clearance_response", "received_packets.csv")
        return response_data.get("result")
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining path clearance: {e}")
        return None


def ObtainGoalHttp(AGV_ID):
    url = MAIN_SERVER_URL + "/get_goal"

    packet_type = 1 
    ''' 1: Goal request, 2: Goal response, 3: Path clearance request, 4: Path clearance response, 
    5: Location update, 6: Location update response, 7: Task End Update, 8: Task End Update response
    9: Interrupt, 10: Interrupt response'''

    global goal_request_id
    goal_request_id += 1
    sent_packet_id = f"agv{AGV_ID}/{packet_type}/{goal_request_id}"
    payload = {"id": sent_packet_id,
               "agv_id": f"agv{AGV_ID}",
               "destination": (0,0), # Dummy values in the format of response from server
               "storage": (0,0,0),# Dummy values in the format of response from server
               "action": 2, # Dummy values in the format of response from server
        }
    # Capture t1 (time when the request is sent)
    t1 = time.time()
    payload["t1"] = t1  # Add t1 to the payload
    payload["t2"] = t1 # Dummy values in the format of response from server
    payload["t3"] = t1 # Dummy values in the format of response from server

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        # Capture t4 (time when the response is received)
        t4 = time.time()

        response_data = response.json()

        recieve_packet_id = response_data.get("id")

        # Read t1, t2, t3 from server response
        t1_server = response_data.get("t1")
        t2 = response_data.get("t2")
        t3 = response_data.get("t3")

        # Save t1, t2, t3, t4 to a CSV file
        SaveCommunicationTime("agv"+str(AGV_ID), t1_server, t2, t3, t4, "get_goal.csv")
        SavePacketData(sent_packet_id, "agv"+str(AGV_ID), "goal_request", "sent_packets.csv")
        SavePacketData(recieve_packet_id, "agv"+str(AGV_ID), "goal_response", "received_packets.csv")
        
        return response_data
    except requests.exceptions.RequestException as e:
        # ---------- print(f"Error obtaining goal: {e}")
        return None
