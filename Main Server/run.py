from flask import Flask, request, jsonify
from server import database  

app = Flask(__name__)


@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Test endpoint is working!"}), 200


# @app.route('/update_agv_location', methods=['POST'])
# def update_agv_location():
#     data = request.json
#     print("Received data:", data)  # Debug log
#     agv = {
#         "agv_id": data["agv_id"],
#         "location": data["location"],
#         "segment": data["segment"],
#         "status": data["status"],
#         "timestamp": data["timestamp"],
#     }
#     database["agvs"].insert_one(agv)
#     print("AGV location saved")  # Debug log
#     return jsonify({"message": "AGV location updated"}), 200


# @app.route('/get_agv_locations', methods=['GET'])
# def get_agv_locations():
#     agvs = list(database["agvs"].find({}))
#     return jsonify(agvs), 200

if __name__ == "__main__":
    app.run(debug=False)
