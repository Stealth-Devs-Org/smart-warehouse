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



def get_all_agvs():
    agvs_collection = database["agvs"]
    agvs_cursor = agvs_collection.find()
    agvs_data = {}
    for agv in agvs_cursor:
        agv_id = agv.get("agv_id")
        agvs_data[agv_id] = {
            "agv_id": agv.get("agv_id"),
            "location": agv.get("location"),
            "segment": agv.get("segment"),
            "status": agv.get("status"),
            "timestamp": agv.get("timestamp"),
        }
    return agvs_data
