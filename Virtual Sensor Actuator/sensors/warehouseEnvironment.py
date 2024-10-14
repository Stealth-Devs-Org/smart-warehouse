import time
import random

warehouse_temperature_values = [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]

warehouse_airquality_values = [0.5, 0.6, 0.7, 0.8, 0.9, 0.8, 0.7]

warehouse_smoke_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3]

warehouse_humidity_values = [0.5, 0.6, 0.7, 0.8, 0.9, 0.8, 0.7]

def main ():
    while True:
        # updateTempValue(partitionNumber)
        print(warehouse_temperature_values)
        time.sleep(1)


if __name__ == "__main__":
    main()