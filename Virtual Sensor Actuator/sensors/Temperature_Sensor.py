import threading
import random
import time
import sys
import json
import paho.mqtt.client as mqtt
from sensorUtils import SetSensorState, sensor_state, ReadVariableFromDatabase



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
    ["(28,18)", "(36,18)", "(28,27)", "(36,27)"],
    
    # Partition 7
    ["(52,13)", "(52,26)", "(46,17)", "(46,24)"]
]


BROKER = "localhost"  
PORT = 1883
TOPIC = "/sensor_temperature"

# client = mqtt.Client()


# def connect_mqtt():
#     client.connect(BROKER, PORT, 60)
#     client.loop_start()  #loop in seperate thread...

class TemperatureSensor(threading.Thread):
    def __init__(self, sensor_id, partition_id):
        threading.Thread.__init__(self)
        self.client = mqtt.Client()
        self.sensor_id = sensor_id
        self.partition_id = partition_id
        self.running = True  

    def connect_mqtt(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()  #loop in seperate thread...
        
    def run(self):
        self.connect_mqtt()
        while self.running:
            temperature = self.get_temperature_value()
            SetSensorState("Temperature", self.sensor_id,  self.partition_id,self.sensor_id, round(temperature, 2), 1)
            print(f"Sensor state: {sensor_state} \n")
            # self.client.publish(TOPIC, str(sensor_state)) 
            self.client.publish(TOPIC, json.dumps(sensor_state))
            time.sleep(1)

    def stop(self):
        self.client.loop_stop()
        self.running = False

    def get_temperature_value(self):
        warehouse_temperature_values = ReadVariableFromDatabase("Temperature Values")
        base_temperature = warehouse_temperature_values[self.partition_id]
        variation = random.uniform(-0.1, 0.1)
        return base_temperature + variation

def main():
    # connect_mqtt()

    no_of_partitions = len(TempsensorID)
    allSensors = []

    for j in range(no_of_partitions):
        allSensors.append([])
        for coord in TempsensorID[j]:
            sensor = TemperatureSensor(sensor_id=coord, partition_id=j)  # Pass partition ID
            allSensors[j].append(sensor) 
            sensor.start()

    try:
        while True:
            time.sleep(1)  
            #print("\nTemperature Sensors are running")
    except KeyboardInterrupt:
        print("\nStopping all sensors...")
        for partition in allSensors:
            for sensor in partition:
                sensor.stop()
        for partition in allSensors:
            for sensor in partition:
                sensor.join()
        print("All sensors stopped.")
        

if __name__ == "__main__":
    main()
