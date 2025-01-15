





import time
import os
import json


# # Desired values (no need to mention them for writing to the database)
# desired_warehouse_temperature_values = [25.0, 25.5, 30.0, 25.5, 23.5, 23.8, 38.1]
# desired_warehouse_airquality_values = [500.0, 520.0, 400.0, 700.0, 650.0, 580.0, 600.0]  # in ppm
# desired_warehouse_smoke_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3]  # binary value?
# desired_warehouse_humidity_values = [45.0, 47.5, 48.0, 49.5, 44.0, 50.2, 46.8]  # in %RH


# For database environment, use the actual (current) values
warehouse_temperature_values = [176.5, 229.2, 195.8, 189.6, 223.9, 208.9, 210.9]
warehouse_airquality_values = [500.0, 520.0, 480.0, 700.0, 650.0, 580.0, 600.0]  # in ppm
warehouse_smoke_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3]  # binary value?
warehouse_humidity_values = [45.0, 47.5, 48.0, 49.5, 44.0, 50.2, 46.8]  # in %RH


# File path setup
directory = 'Virtual Sensor Actuator'
filename = 'warehouse_Env_data.json'
filepath = os.path.join(directory, filename)


# def writeToDatabase():  # Writing to the database file for the first time
#     global warehouse_temperature_values, warehouse_airquality_values, warehouse_smoke_values, warehouse_humidity_values
#     data = {
#         "Temperature Values": warehouse_temperature_values,
#         "AirQuality Values": warehouse_airquality_values,
#         "Humidity Values": warehouse_humidity_values
#     }
    
#     with open(filepath, 'w') as file:
#         json.dump(data, file, indent=4)  # Writing in JSON format with indentation


def ReadFromDatabase():
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    # Read values from the JSON data
    read_temperature_values = data.get("Temperature Values", [])
    read_airquality_values = data.get("AirQuality Values", [])
    read_humidity_values = data.get("Humidity Values", [])
    
    # Print the read values
    print("Temperature Values:", read_temperature_values)
    print("Air Quality Values:", read_airquality_values)
    print("Humidity Values:", read_humidity_values)
    print("\n\n")


if __name__ == "__main__":
    # writeToDatabase()  # Uncomment for writing first time
    print("Data written to file 'warehouse_Env_data.json'")
    
    while True:
        ReadFromDatabase()
        time.sleep(3)
