from flask import Flask, render_template, jsonify
import math
import json
from flask import request

app = Flask(__name__)

# Store heat and air quality points
heat_points = []
air_quality_points = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_heat_point', methods=['POST'])
def add_heat_point():
    data = request.json
    heat_points.append(data)
    return jsonify({'success': True})

@app.route('/add_air_quality_point', methods=['POST'])
def add_air_quality_point():
    data = request.json
    air_quality_points.append(data)
    return jsonify({'success': True})

@app.route('/delete_points', methods=['POST'])
def delete_points():
    data = request.json
    global heat_points, air_quality_points
    x1, y1, x2, y2 = data['x1'], data['y1'], data['x2'], data['y2']
    heat_points = [p for p in heat_points if not (x1 <= p['x'] <= x2 and y1 <= p['y'] <= y2)]
    air_quality_points = [p for p in air_quality_points if not (x1 <= p['x'] <= x2 and y1 <= p['y'] <= y2)]
    return jsonify({'success': True})

@app.route('/measure', methods=['POST'])
def measure():
    data = request.json
    x, y = data['x'], data['y']
    env_temp = data['env_temp']
    total_heat = calculate_heat_at_point(x, y)
    total_air_quality = calculate_air_quality_at_point(x, y)
    final_temp = max(total_heat, env_temp)
    return jsonify({'heat': final_temp, 'air_quality': total_air_quality})

@app.route('/clear_all', methods=['POST'])
def clear_all():
    global heat_points, air_quality_points
    heat_points = []
    air_quality_points = []
    return jsonify({'success': True})

def calculate_heat_at_point(x, y):
    total_heat = 0
    for point in heat_points:
        distance = math.sqrt((x - point['x']) ** 2 + (y - point['y']) ** 2)
        if distance <= point['radius']:
            gradient = max(0, (point['radius'] - distance) / point['radius'])
            contribution = point['value'] * gradient
            total_heat = max(total_heat, contribution)
    return total_heat

def calculate_air_quality_at_point(x, y):
    total_air_quality = 0
    for point in air_quality_points:
        distance = math.sqrt((x - point['x']) ** 2 + (y - point['y']) ** 2)
        if distance <= point['radius']:
            gradient = max(0, (point['radius'] - distance) / point['radius'])
            contribution = point['value'] * gradient
            total_air_quality = max(total_air_quality, contribution)
    return total_air_quality

if __name__ == '__main__':
    app.run(debug=True)
