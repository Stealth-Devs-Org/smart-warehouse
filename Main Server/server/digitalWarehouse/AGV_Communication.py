from flask import Flask, jsonify
from flask import Blueprint
from agv.db_operations import get_all_agvs

app = Flask(__name__)

agvWarehouse = Blueprint("agvWarehouse", __name__)


agvs_data = get_all_agvs()



# agvs_data = {
#     "agv1": {
#         "agv_id": "agv1",
#         "location": [1, 2],
#         "segment": [[1, 2], [1, 3], [1, 4]],
#         "status": 1,
#         "timestamp": "2023-10-01T12:34:56Z",
#     },
#     "agv2": {
#         "agv_id": "agv2",
#         "location": [5, 3],
#         "segment": [[5, 3], [4, 3], [3, 3], [2, 3], [1, 3]],
#         "status": 1,
#         "timestamp": "2023-10-01T12:34:56Z",
#     },
#     "agv3": {
#         "agv_id": "agv3",
#         "location": [1, 4],
#         "segment": [[1, 4], [2, 4], [3, 4]],
#         "status": 1,
#         "timestamp": "2023-10-01T12:34:56Z",
#     },
#     "agv4": {
#         "agv_id": "agv4",
#         "location": [4, 5],
#         "segment": [[4, 5], [4, 6], [4, 7]],
#         "status": 1,
#         "timestamp": "2023-10-01T12:34:56Z",
#     },
# }


@agvWarehouse.route('/AGV_Communications', methods=['GET'])
def get_agvs():
    return jsonify(agvs_data)

if __name__ == '__main__':
    app.run(debug=True)
