import threading
import random
import sys
import time
import paho.mqtt.client as mqtt
from sensorUtils import SetSensorState, sensor_state, ReadVariableFromDatabase

# Sensor ID for each partition (as coordinate)
HumiditysensorID = [
    # No Partition for Humidity    
    
    ["(4,3)", "(4,9)", "(3,22)", "(15,23)", "(36,6)"]
]


BROKER = "localhost"  
PORT = 1883
TOPIC = "/sensor_humidity"

client = mqtt.Client()


def connect_mqtt():
    client.connect(BROKER, PORT, 60)
    client.loop_start()  #loop in seperate thread...

class HumiditySensor(threading.Thread):
    def __init__(self, sensor_id, partition_id):
        threading.Thread.__init__(self)
        # self.client = mqtt.Client()
        self.sensor_id = sensor_id
        self.partition_id = partition_id
        self.running = True  

    # def connect_mqtt(self):
    #     self.client.connect(BROKER, PORT, 60)
    #     self.client.loop_start()  #loop in seperate thread...
        
    def run(self):
        while self.running:
            humidity = self.get_humidity_value()
            SetSensorState("Humidity", self.sensor_id,  self.partition_id,self.sensor_id, round(humidity, 2), 1)
            print(f"Sensor state: {sensor_state}")
            client.publish(TOPIC, str(sensor_state))
            time.sleep(1)

    def stop(self):
        self.running = False
        self.client.loop_stop()

    def get_humidity_value(self):
        warehouse_airquality_values = ReadVariableFromDatabase("Humidity Values")
        base_humidty = warehouse_humidity_values[self.partition_id]
        variation = random.uniform(-0.1, 0.1)   
        return base_humidty + variation

def main():
    connect_mqtt()

    no_of_partitions = len(HumiditysensorID)
    allSensors = []

    for j in range(no_of_partitions):
        allSensors.append([])
        for coord in HumiditysensorID[j]:
            sensor = HumiditySensor(sensor_id=coord, partition_id=j)  # Pass partition ID
            allSensors[j].append(sensor) 
            sensor.start()

    try:
        while True:
            time.sleep(1)  
            #print("\nHumidity Sensors are running")
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






















import threading
import random
import time
import json
import paho.mqtt.client as mqtt
from sensorUtils import SetSensorState, sensor_state, ReadVariableFromDatabase

# Sensor ID for each partition (as coordinate)
HumiditysensorID = [
    ["(4,3)", "(4,9)", "(3,22)", "(15,23)", "(36,6)"]
]

BROKER = "localhost"
PORT = 1883
TOPIC = "/sensor_humidity"

class HumiditySensor(threading.Thread):
    def __init__(self, sensor_id, partition_id):
        threading.Thread.__init__(self)
        self.client = mqtt.Client()
        self.sensor_id = sensor_id
        self.partition_id = partition_id
        self.running = True

    def connect_mqtt(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()

    def run(self):
        self.connect_mqtt()
        while self.running:
            try:
                humidity = self.get_humidity_value()
                SetSensorState("Humidity", self.sensor_id, self.partition_id, self.sensor_id, round(humidity, 2), 1)
                print(f"Sensor state: {sensor_state} \n")
                self.client.publish(TOPIC, json.dumps(sensor_state))
                time.sleep(random.uniform(1, 1.5))
            except Exception as e:
                print(f"Error in sensor {self.sensor_id}: {e}")
                self.running = False  # Stop the sensor if an error occurs

    def stop(self):
        self.client.loop_stop()
        self.running = False

    def get_humidity_value(self):
        warehouse_humidity_values = ReadVariableFromDatabase("Humidity Values")
        if not warehouse_humidity_values:
            print("Error: Humidity values not found in the database.")
            return 0
        base_humidity = warehouse_humidity_values[self.partition_id]
        variation = random.uniform(0, 0.4)
        return base_humidity + variation

def monitor_sensors(allSensors):
    while True:
        for partition in allSensors:
            for sensor in partition:
                if not sensor.running:
                    print(f"Restarting sensor {sensor.sensor_id} in partition {sensor.partition_id}")
                    new_sensor = HumiditySensor(sensor.sensor_id, sensor.partition_id)
                    partition.remove(sensor)
                    partition.append(new_sensor)
                    new_sensor.start()
        time.sleep(2)

def main():
    no_of_partitions = len(HumiditysensorID)
    allSensors = []

    for j in range(no_of_partitions):
        allSensors.append([])
        for coord in HumiditysensorID[j]:
            sensor = HumiditySensor(sensor_id=coord, partition_id=j)
            allSensors[j].append(sensor)
            sensor.start()

    monitor_thread = threading.Thread(target=monitor_sensors, args=(allSensors,), daemon=True)
    monitor_thread.start()

    try:
        while True:
            time.sleep(1)
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
