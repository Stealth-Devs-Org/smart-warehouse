import threading
import time
from datetime import datetime, timedelta, timezone

from server.agv.utils import (
    Update_agv_json,
    Update_permanent_obstacles_json,
    Update_sent_interrupt_json,
    Update_working_agvs_json,
)

permanent_obstacles = {}


def remove_timeout_agvs():

    def check_agvs():
        from server.agv.col_avoid import agvs_data, sent_interrupts
        from server.agv.scheduler import working_agvs

        while True:
            # agvs_data = Get_values_from_agv_json()
            # sent_interrupts = Get_values_from_sent_interrupt_json()
            # permanent_obstacles = Get_values_from_permanent_obstacles_json()
            # working_agvs = Get_values_from_working_agvs_json()
            for agv_id in list(agvs_data.keys()):
                timestamp = datetime.fromisoformat(agvs_data[agv_id]["timestamp"]).replace(
                    tzinfo=timezone.utc
                )
                if timestamp < datetime.now(timezone.utc) - timedelta(seconds=30):
                    permanent_obstacles[agv_id] = agvs_data[agv_id]["location"]
                    del agvs_data[agv_id]
                    # agvs_data[agv_id] = None
                    if agv_id in sent_interrupts.keys():
                        del sent_interrupts[agv_id]
                        # sent_interrupts[agv_id] = None
                    if agv_id in working_agvs.keys():
                        del working_agvs[agv_id]
                        # working_agvs[agv_id] = None
                    print("AGV", agv_id, "is timed out")
                    Update_agv_json(agvs_data)
                    Update_sent_interrupt_json(sent_interrupts)
                    Update_permanent_obstacles_json(permanent_obstacles)
                    Update_working_agvs_json(working_agvs)
            time.sleep(1)  # Sleep for a while before checking again

    thread = threading.Thread(target=check_agvs)
    thread.daemon = True  # Daemonize thread to exit when main program exits
    thread.start()


def remove_from_permanent_obstacles(agv_id):
    from server.agv.keep_alive import permanent_obstacles

    # permanent_obstacles = Get_values_from_permanent_obstacles_json()

    if agv_id in permanent_obstacles.keys():
        del permanent_obstacles[agv_id]
        # permanent_obstacles[agv_id] = None
        # Update_permanent_obstacles_json(permanent_obstacles)
        print("AGV", agv_id, "is back alive")

    return permanent_obstacles


def save_main_server_data_in_json(interval):
    from server.agv.col_avoid import agvs_data, sent_interrupts
    from server.agv.scheduler import working_agvs

    while True:
        Update_agv_json(agvs_data)
        # print(agvs_data.keys())
        Update_sent_interrupt_json(sent_interrupts)
        Update_working_agvs_json(working_agvs)
        Update_permanent_obstacles_json(permanent_obstacles)
        time.sleep(interval)  # Save data every 1 seconds


def start_saving_data_thread(interval=1):
    thread = threading.Thread(target=save_main_server_data_in_json, args=(interval,))
    thread.daemon = True  # Daemonize thread to exit when main program exits
    thread.start()
