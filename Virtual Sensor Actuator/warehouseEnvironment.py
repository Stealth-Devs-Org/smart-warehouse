import time
from multiprocessing import Value

# for Actuator...............................................

desired_warehouse_temperature_values = [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]

desired_warehouse_airquality_values = [500, 520, 480, 700, 650, 580, 600] # in ppm

desired_warehouse_smoke_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3] # binary value?

desired_warehouse_humidity_values = [45.0, 47.5, 48.0, 49.5, 44.0, 50.2, 46.8]  # in %RH




warehouse_temperature_values = [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]

warehouse_airquality_values = [500, 520, 480, 700, 650, 580, 600] # in ppm

warehouse_smoke_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3] # binary value?

warehouse_humidity_values = [45.0, 47.5, 48.0, 49.5, 44.0, 50.2, 46.8]  # in %RH

def main ():
    while True:
        # updateTempValue(partitionNumber)
        print(warehouse_temperature_values)
        time.sleep(1)


if __name__ == "__main__":
    main()