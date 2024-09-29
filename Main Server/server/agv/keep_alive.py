import threading
import time
from datetime import datetime, timedelta, timezone

from server.agv.scheduler import working_agvs
from server.agv.utils import (
    Get_values_from_agv_json,
    Get_values_from_permanent_obstacles_json,
    Get_values_from_sent_interrupt_json,
    Update_agv_json,
    Update_permanent_obstacles_json,
    Update_sent_interrupt_json,
)


def remove_timeout_agvs():

    def check_agvs():
        while True:
            agvs_data = Get_values_from_agv_json()
            sent_interrupts = Get_values_from_sent_interrupt_json()
            permanent_obstacles = Get_values_from_permanent_obstacles_json()
            for agv_id in list(agvs_data.keys()):
                timestamp = datetime.fromisoformat(agvs_data[agv_id]["timestamp"]).replace(
                    tzinfo=timezone.utc
                )
                if timestamp < datetime.now(timezone.utc) - timedelta(seconds=15):
                    permanent_obstacles[agv_id] = agvs_data[agv_id]["location"]
                    agvs_data[agv_id] = None
                    if agv_id in sent_interrupts.keys():
                        sent_interrupts[agv_id] = None
                    if agv_id in working_agvs.keys():
                        del working_agvs[agv_id]
                    print("AGV", agv_id, "is timed out")
                    Update_agv_json(agvs_data)
                    Update_sent_interrupt_json(sent_interrupts)
                    Update_permanent_obstacles_json(permanent_obstacles)
            time.sleep(1)  # Sleep for a while before checking again

    thread = threading.Thread(target=check_agvs)
    thread.start()


def remove_from_permanent_obstacles(agv_id):
    permanent_obstacles = Get_values_from_permanent_obstacles_json()

    if agv_id in permanent_obstacles.keys():
        permanent_obstacles[agv_id] = None
        Update_permanent_obstacles_json(permanent_obstacles)
        print("AGV", agv_id, "is back alive")

    return permanent_obstacles
