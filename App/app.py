from flask import Flask, render_template, request, jsonify
from PIL import Image
import os
import math

app = Flask(__name__)



# To store heat and air quality points
heat_points = []
air_quality_points = []

# Function to calculate heat
def calculate_heat_at_point(x, y, points):
    total_heat = 0
    for _, heat_x, heat_y, heat_radius, heat_value in points:
        distance = math.sqrt((x - heat_x) ** 2 + (y - heat_y) ** 2)
        if distance <= heat_radius:
            gradient = max(0, (heat_radius - distance) / heat_radius)
            contribution = heat_value * gradient
            total_heat = max(total_heat, contribution)
    return total_heat

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_floor_plan():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = os.path.join('static/images', file.filename)
        file.save(filename)
        return jsonify({"message": "File uploaded", "file_path": filename}), 200
    
@app.route('/Sensors&Actuators')
def Sensors():
    return render_template('Sensors & Actuators.html')



@app.route('/MainServer')
def Mainserver():
    return render_template('Main Server.html')

@app.route('/AutomateGuidedVehicles')
def agv():
    return render_template('Automate Guided Vehicles.html')

@app.route('/NetworkMonitoring')
def NetworkMonitoring():
    return render_template('Network_Monitoring.html')




# API to add heat/air quality points
@app.route('/add_point', methods=['POST'])
def add_point():
    data = request.get_json()
    point_type = data['type']
    x, y = data['x'], data['y']
    radius, value = data['radius'], data['value']
    
    point = (x, y, radius, value)
    if point_type == "heat":
        heat_points.append(point)
    elif point_type == "air_quality":
        air_quality_points.append(point)
    
    return jsonify({"message": "Point added"}), 200

# More routes to handle measurement, deletion, etc.


if __name__ == '__main__':
    app.run(debug=True)