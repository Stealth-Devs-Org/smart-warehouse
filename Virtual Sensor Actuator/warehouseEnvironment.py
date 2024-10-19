import time
import os


# for Actuator...............................................

desired_warehouse_temperature_values = [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 38.1]

desired_warehouse_airquality_values = [500.0, 520.0, 480.0, 700.0, 650.0, 580.0, 600.0] # in ppm

desired_warehouse_smoke_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3] # binary value?

desired_warehouse_humidity_values = [45.0, 47.5, 48.0, 49.5, 44.0, 50.2, 46.8]  # in %RH



# for database environment...............................................

warehouse_temperature_values = [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]

warehouse_airquality_values = [500.0, 520.0, 480.0, 700.0, 650.0, 580.0, 600.0] # in ppm

warehouse_smoke_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3] # binary value?

warehouse_humidity_values = [45.0, 47.5, 48.0, 49.5, 44.0, 50.2, 46.8]  # in %RH

# def main ():
#     while True:
#         # updateTempValue(partitionNumber)
#         print(warehouse_temperature_values)
#         time.sleep(1)


directory = 'Virtual Sensor Actuator'
filename = 'warehouse_Env_data.txt'
filepath = os.path.join(directory, filename)

# def writeToDatabase():      # uncomment this and a write function in main to write data to file only first time.
#     global warehouse_temperature_values, warehouse_airquality_values, warehouse_smoke_values, warehouse_humidity_values
#     with open(filepath, 'w') as file:
#         file.write("Temperature Values :\n")
#         file.write(', '.join(map(str, warehouse_temperature_values)) + "\n\n")
        
#         file.write("AirQuality Values :\n")
#         file.write(', '.join(map(str, warehouse_airquality_values)) + "\n\n")
        
#         file.write("Smoke Values :\n")
#         file.write(', '.join(map(str, warehouse_smoke_values)) + "\n\n")
        
#         file.write("Humidity Values :\n")
#         file.write(', '.join(map(str, warehouse_humidity_values)) + "\n")


def ReadFromDatabase():
    with open(filepath, 'r') as file:
        lines = file.readlines()

    read_temperature_values = []
    read_airquality_values = []
    read_smoke_values = []
    read_humidity_values = []

    for i, line in enumerate(lines):
        if "Temperature Values" in line:
            read_temperature_values = list(map(float, lines[i + 1].strip().split(', ')))
        elif "AirQuality Values" in line:
            read_airquality_values = list(map(float, lines[i + 1].strip().split(', ')))
        elif "Smoke Values" in line:
            read_smoke_values = list(map(float, lines[i + 1].strip().split(', ')))
        elif "Humidity Values" in line:
            read_humidity_values = list(map(float, lines[i + 1].strip().split(', ')))

    print("Temperature Values:", read_temperature_values)
    print("Air Quality Values:", read_airquality_values)
    print("Smoke Values:", read_smoke_values)
    print("Humidity Values:", read_humidity_values)

    print("\n\n")

            





if __name__ == "__main__":
    # writeToDatabase()
    print("Data written to file 'warehouse_data.txt'")
    while True:
        ReadFromDatabase()
        time.sleep(3)
    