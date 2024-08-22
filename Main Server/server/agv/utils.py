from server import database


def save_agv_location(data):
    agv = {
        "agv_id": data["agv_id"],
        "location": data["location"],
        "timestamp": data["timestamp"]
    }
    database["agvs"].insert_one(agv)
