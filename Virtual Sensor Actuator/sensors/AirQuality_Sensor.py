import threading
import random
import time
import json
import paho.mqtt.client as mqtt
from sensorUtils import SetSensorState, sensor_state, ReadVariableFromDatabase, SaveToCSV

# Sensor ID for each partition (as coordinate)
AirQualitysensorID = [
    [],# ["(2,4)", "(2,8)"],
    ["(14,11)", "(14,3)", "(14,11)", "(14,3)"],
    # ["(34,11)", "(34,3)", "(34,11)", "(34,3)"],
    # ["(3,16)", "(3,26)", "(3,26)", "(3,16)"],
    # ["(15,27)", "(15,17)", "(15,27)", "(15,17)"],
    # ["(32,18)", "(32,27)", "(32,27)", "(32,18)"],
    # ["(49,14)", "(49,27)", "(49,14)", "(49,27)"]
]

BROKER = "localhost" # "192.168.1.12"
PORT = 1883
TOPIC = "/sensor_air_quality"
TOPICtoSubscribe = "/sensor_timestamps"

class AirQualitySensor(threading.Thread):
    def __init__(self, sensor_id, partition_id):
        threading.Thread.__init__(self)
        self.client = mqtt.Client()
        self.sensor_id = sensor_id
        self.partition_id = partition_id
        self.running = True

    def connect_mqtt(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()
        self.client.subscribe(TOPICtoSubscribe, qos=1)
        self.client.on_message = self.on_message

    def on_message(self, client, userdata, message):
        t4 = time.time()
        if message.topic == TOPICtoSubscribe:
            payload = message.payload.decode()
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                print(f"Invalid JSON received on topic {message.topic}: {payload}")
                return
            if data.get("sensor_id") == self.sensor_id and data.get("sensor_type") == "AirQuality":
                print(f"Received message on topic {message.topic}: {payload}")
                SaveToCSV(data, t4, "sensorTimestamps.csv")

    def run(self):
        self.connect_mqtt()
        while self.running:
            try:
                air_quality = self.get_air_quality_value()
                t1 = time.time()
                SetSensorState("AirQuality", self.sensor_id, self.partition_id, self.sensor_id, round(air_quality, 2), 1, t1)
                print(f"Sensor state: {sensor_state} \n")
                self.client.publish(TOPIC, json.dumps(sensor_state), qos=1)
                time.sleep(random.uniform(1, 1.5))
            except Exception as e:
                print(f"Error in sensor {self.sensor_id}: {e}")
                self.running = False  # Stop the sensor if an error occurs

    def stop(self):
        self.client.loop_stop()
        self.running = False

    def get_air_quality_value(self):
        warehouse_air_quality_values = ReadVariableFromDatabase("AirQuality Values")
        if not warehouse_air_quality_values:
            print("Error: Air quality values not found in the database.")
            return 0
        base_air_quality = warehouse_air_quality_values[self.partition_id]
        variation = random.uniform(5, 10)
        return base_air_quality + variation

def monitor_sensors(allSensors):
    while True:
        for partition in allSensors:
            for sensor in partition:
                if not sensor.running:
                    print(f"Restarting sensor {sensor.sensor_id} in partition {sensor.partition_id}")
                    new_sensor = AirQualitySensor(sensor.sensor_id, sensor.partition_id)
                    partition.remove(sensor)
                    partition.append(new_sensor)
                    new_sensor.start()
        time.sleep(2)

def main():
    no_of_partitions = len(AirQualitysensorID)
    allSensors = []

    for j in range(no_of_partitions):
        allSensors.append([])
        for coord in AirQualitysensorID[j]:
            sensor = AirQualitySensor(sensor_id=coord, partition_id=j)
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
