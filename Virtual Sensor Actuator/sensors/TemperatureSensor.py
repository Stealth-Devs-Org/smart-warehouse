import threading
import random
import time



class TemperatureSensor(threading.Thread):
    def __init__(self, sensor_id, min_temp, max_temp):
        threading.Thread.__init__(self)
        self.sensor_id = sensor_id
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.running = True

    def run(self):
        while self.running:
            temperature = random.uniform(self.min_temp, self.max_temp)
            print(f"Sensor {self.sensor_id}: {temperature:.2f}°C\n")
            time.sleep(1)

    def stop(self):
        self.running = False

def main():
    no_of_partitions = 7
    no_of_sensors_in_each_part= [3,4,5,6,7,8,9]
    allSensors=[]
    
    num_sensors = 5  # Number of sensors
    min_temp = -40.0  # Minimum temperature
    max_temp = 40.0  # Maximum temperature

    for j in range (no_of_partitions):
        allSensors.append([])

        for i in range(no_of_sensors_in_each_part[j]):
            sensor = TemperatureSensor(sensor_id=f"ID ({j},{i})", min_temp=min_temp, max_temp=max_temp)
            allSensors[j].append(sensor)
            sensor.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        for partition in allSensors:
            for sensor in partition:
                sensor.stop()
            for sensor in partition:
                sensor.join()

if __name__ == "__main__":
    main()