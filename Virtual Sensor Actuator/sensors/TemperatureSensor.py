import threading
import random
import time
# from flask import Flask, request, jsonify

from warehouseEnvironment import warehouse_temperature_values
from sensorUtils import SetSensorState, sensor_state
    

#climate_temperature_values = [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]

# Sensor ID for each partition (as coordinate)
TempsensorID = [
    # Partition 1
    ["(2,2)", "(2,10)"],
    
    # Partition 2
    ["(9,11)", "(19,11)", "(19,3)", "(9,3)"],
    
    # Partition 3
    ["(28,11)", "(41,11)", "(28,3)", "(41,3)"],
    
    # Partition 4
    ["(5,15)", "(2,28)", "(5,28)", "(2,19)"],
    
    # Partition 5
    ["(12,27)", "(19,27)", "(19,17)", "(12,17)"],
    
    # Partition 6
    ["(52,13)", "(52,26)", "(46,17)", "(46,24)"],
    
    # Partition 7
    ["(28,18)", "(36,18)", "(28,27)", "(36,27)"]
]

class TemperatureSensor(threading.Thread):
    def __init__(self, sensor_id, partition_id):
        threading.Thread.__init__(self)
        self.sensor_id = sensor_id
        self.partition_id = partition_id
        self.running = True  
        

    def run(self):
        while self.running:
            temperature = self.get_temperature_value()
            #print(f"\nSensor {self.sensor_id}: {temperature:.2f}°C")
            SetSensorState("Temperature", self.sensor_id, self.sensor_id,self.partition_id, round(temperature,2), 1)
            print(f"Sensor state: {sensor_state}")
            time.sleep(1)

    def stop(self):
        self.running = False

    def get_temperature_value(self):
        global warehouse_temperature_values
        base_temperature = warehouse_temperature_values[self.partition_id]
        variation = random.uniform(-0.1, 0.1)
        return base_temperature + variation

def main():

    no_of_partitions = len(TempsensorID)
    allSensors = []

    for j in range(no_of_partitions):
        allSensors.append([])
        for coord in TempsensorID[j]:
            sensor = TemperatureSensor(sensor_id=coord, partition_id=j)  # Pass partition ID
            allSensors[j].append(sensor) 
            sensor.start()

    
    while True:
        time.sleep(0.1)  

if __name__ == "__main__":
    main()

