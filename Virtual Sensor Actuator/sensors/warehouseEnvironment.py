# from flask import Flask, request, jsonify
# from TemperatureSensor import sensor_state

# app = Flask(__name__)

warehouse_temperature_values = [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]

partitionNumber = 3
newTempValue = 30

# def updateTempValue (partID,value):
#     global warehouse_temperature_values
#     warehouse_temperature_values[partID-1] = value


# @app.route('/tempState', methods=['GET'])
# def get_temp_state():
#     return jsonify(sensor_state)



# if __name__ == "__main__":
#     app.run(debug=True)