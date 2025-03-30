import threading
import random
import time
import json
import paho.mqtt.client as mqtt
from sensorUtils import SetSensorState, sensor_state, ReadVariableFromDatabase

SmokesensorID = [
    # No Partition for Smoke (same layout as HumiditySensor for consistency; adjust if needed)
    ["(2,6)"], 
    ["(14,7)"], 
    ["(36,6)"],
    ["(3,22)"], 
    ["(15,23)"], 
    ["(32,21)"],
    ["(49,21)"]
]

BROKER = "localhost"
PORT = 1883
TOPIC = "/sensor_smoke"

class SmokeSensor(threading.Thread):
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
                smoke = self.get_smoke_value()
                SetSensorState("Smoke", self.sensor_id, self.partition_id, self.sensor_id, round(smoke, 4), 1)
                print(f"Sensor state: {sensor_state} \n")
                self.client.publish(TOPIC, json.dumps(sensor_state))
                time.sleep(random.uniform(1, 1.5))
            except Exception as e:
                print(f"Error in sensor {self.sensor_id}: {e}")
                self.running = False  # Stop the sensor if an error occurs

    def stop(self):
        self.client.loop_stop()
        self.running = False

    def get_smoke_value(self):
        warehouse_smoke_values = ReadVariableFromDatabase("Smoke Values")
        if not warehouse_smoke_values:
            print("Error: Smoke values not found in the database.")
            return 0
        base_smoke = warehouse_smoke_values[self.partition_id]
        variation = random.uniform(0, 0.001)  
        return base_smoke + variation

def monitor_sensors(allSensors):
    while True:
        for partition in allSensors:
            for sensor in partition:
                if not sensor.running:
                    print(f"Restarting sensor {sensor.sensor_id} in partition {sensor.partition_id}")
                    new_sensor = SmokeSensor(sensor.sensor_id, sensor.partition_id)
                    partition.remove(sensor)
                    partition.append(new_sensor)
                    new_sensor.start()
        time.sleep(2)

def main():
    no_of_partitions = len(SmokesensorID)
    allSensors = []

    for j in range(no_of_partitions):
        allSensors.append([])
        for coord in SmokesensorID[j]:
            sensor = SmokeSensor(sensor_id=coord, partition_id=j)
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