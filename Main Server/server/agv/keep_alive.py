import threading
import time
from datetime import datetime, timedelta

from server.agv.col_avoid import agvs_data, sent_interrupts
from server.agv.scheduler import working_agvs

permanent_obstacles = {}


def remove_timeout_agvs():
    global agvs_data
    global sent_interrupts

    while True:
        for agv_id in list(agvs_data.keys()):
            timestamp = datetime.fromisoformat(agvs_data[agv_id]["timestamp"])
            if timestamp < datetime.now() - timedelta(seconds=15):
                permanent_obstacles[agv_id] = agvs_data[agv_id]["location"]
                del agvs_data[agv_id]
                if agv_id in sent_interrupts.keys():
                    del sent_interrupts[agv_id]
                if agv_id in working_agvs.keys():
                    del working_agvs[agv_id]
                print("AGV", agv_id, "is timed out")
        time.sleep(1)  # Sleep for a while before checking again


# Start the remove_timeout_agvs function in a separate thread
thread = threading.Thread(target=remove_timeout_agvs)
thread.daemon = True
thread.start()


def remove_from_permanent_obstacles(agv_id):
    global permanent_obstacles

    if agv_id in permanent_obstacles.keys():
        del permanent_obstacles[agv_id]
        print("AGV", agv_id, "is back alive")

    return permanent_obstacles
