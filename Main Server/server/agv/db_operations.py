from server import database


def save_agv_location(data):
    agv = {
        "agv_id": data["agv_id"],
        "location": data["location"],
        "segment": data["segment"],
        "status": data["status"],  # 0: idle, 1: moving, 2: loading, 3: unloading
        "timestamp": data["timestamp"],
    }
    database["agvs"].insert_one(agv)
