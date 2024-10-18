import threading
import random
import time
import sys
import paho.mqtt.client as mqtt
from sensorUtils import SetSensorState, sensor_state

sys.path.append('Virtual Sensor Actuator')
from warehouseEnvironment import warehouse_airquality_values

# Sensor ID for each partition (as coordinate)
AirQualitysensorID = [
    # Partition 1
    ["(2,4)", "(2,8)"],
    
    # Partition 2
    ["(14,11)", "(14,3)", "(14,11)", "(14,3)"],
    
    # Partition 3
    ["(34,11)", "(34,3)", "(34,11)", "(34,3)"],
    
    # Partition 4
    ["(3,16)", "(3,26)", "(3,26)", "(3,16)"],
    
    # Partition 5
    ["(15,27)", "(15,17)", "(15,27)", "(15,17)"],
    
    # Partition 6
    ["(32,18)", "(32,27)", "(32,27)", "(32,18)"],
    
    # Partition 7
    ["(49,14)", "(49,27)", "(49,14)", "(49,27)"]
]



BROKER = "localhost"  
PORT = 1883
TOPIC = "/sensor_airquality"

#client = mqtt.Client()


# def connect_mqtt():
#     client.connect(BROKER, PORT, 60)
#     client.loop_start()  #loop in seperate thread...

class AirQualitySensor(threading.Thread):
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
            airquality = self.get_airquality_value()
            SetSensorState("AirQuality", self.sensor_id, self.sensor_id, self.partition_id, round(airquality, 2), 1)
            #print(f"ClientID={self.client}")
            print(f"Sensor state: {sensor_state}")
            self.client.publish(TOPIC, str(sensor_state)) 
            time.sleep(1)

    def stop(self):
        self.running = False
        self.client.loop_stop()

    def get_airquality_value(self):
        global warehouse_airquality_values
        base_airquality = warehouse_airquality_values[self.partition_id]
        variation = random.uniform(-0.1, 0.1)
        return base_airquality + variation

def main():
    

    no_of_partitions = len(AirQualitysensorID)
    allSensors = []

    for j in range(no_of_partitions):
        allSensors.append([])
        for coord in AirQualitysensorID[j]:
            sensor = AirQualitySensor(sensor_id=coord, partition_id=j)  # Pass partition ID
            allSensors[j].append(sensor) 
            sensor.start()

    try:
        while True:
            time.sleep(1)  
            #print("\nAir Quality Sensors are running")
    except KeyboardInterrupt:
        print("\nStopping all sensors...")
        for partition in allSensors:
            for sensor in partition:
                sensor.stop()
        for partition in allSensors:
            for sensor in partition:
                sensor.join()
        print("All sensors stopped.")
        #client.loop_stop()  # Stop the MQTT loop

if __name__ == "__main__":
    main()
