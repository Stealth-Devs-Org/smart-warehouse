import time
import random

warehouse_temperature_values = [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]

partitionNumber = 0

# def updateTempValue (partID):
    
#     global warehouse_temperature_values
#     warehouse_temperature_values[partID-1]

def main ():
    while True:
        # updateTempValue(partitionNumber)
        print(warehouse_temperature_values)
        time.sleep(1)


if __name__ == "__main__":
    main()