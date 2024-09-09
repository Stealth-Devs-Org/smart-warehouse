import random
from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock goal mapping based on AGV_ID
goal_mapping = {
    1: [(37, 22)],
    2: [(23, 28)]
    # Add more AGV_ID to goal mappings here
}


@app.route('/get_goal', methods=['POST'])
def get_goal():
    data = request.json
    agv_id = data.get('AGV_ID')
    # Determine the goal based on the AGV_ID
    goal = goal_mapping.get(agv_id, (0, 0)) [0] # Default goal if AGV_ID is not found
    return jsonify({'goal': goal})

@app.route('/path_clearance', methods=['POST'])
def path_clearance():
    data = request.json
    agv_id = data.get('agv_id')
    segment = data.get('segment')
    print('segment',segment)
    if not segment or len(segment) != 2:
        return "Invalid segment", 400

    start_point = segment[0]
    end_point = segment[1]

    # Generate all points in the segment
    points = []
    for x in range(start_point[0], end_point[0] + 1):
        for y in range(start_point[1], end_point[1] + 1):
            points.append((x, y))
    print('points',points)

    # Randomly choose between '1', '2', or a point from the segment
    # obstacle = "["+str(random.choice(points))+"]"
    #choices = ['1'] 
    if (17,22) in points:
        choices ='[(17,22)]'
    else:
        print("no obstacle")
        choices = '1'
    #choices.append(obstacle)
    #result = random.choice(choices)
    
    return choices
    return result
if __name__ == '__main__':
    app.run(debug=True)
