import threading
import random
import time

climate = "winter"

def change_climate():
    global climate
    climates = ['winter', 'spring', 'summer']
    current_index = 0
    while True:
        climate = climates[current_index]
        #print(f"\nClimate changed to: {climate}\n")
        current_index = (current_index + 1) % len(climates)  # Cycle through the list
        time.sleep(10)


# sensor ID for each partition
sensorID = [
    ["(3,1)", "(3,1)", "(3,1)", "(3,1)", "(3,1)", "(3,1)", "(3,1)"],
    ["(4,1)", "(4,1)", "(4,1)", "(4,1)", "(4,1)", "(4,1)", "(4,1)"],
    ["(5,1)", "(5,1)", "(5,1)", "(5,1)", "(5,1)", "(5,1)", "(5,1)"],
    ["(6,1)", "(6,1)", "(6,1)", "(6,1)", "(6,1)", "(6,1)", "(6,1)"],
    ["(4,1)", "(4,1)", "(4,1)", "(4,1)", "(4,1)", "(4,1)", "(7,1)"],
    ["(4,1)", "(4,1)", "(4,1)", "(4,1)", "(4,1)", "(4,1)", "(8,1)"],
    ["(4,1)", "(4,1)", "(4,1)", "(4,1)", "(4,1)", "(4,1)", "(9,1)"]
]


class TemperatureSensor(threading.Thread):
    def __init__(self, sensor_id):
        threading.Thread.__init__(self)
        self.sensor_id = sensor_id
        self.running = True

    def run(self):
        while self.running:
            self.update_temperature_range()
            temperature = random.uniform(self.min_temp, self.max_temp)
            print(f"Sensor {self.sensor_id}: {temperature:.2f}°C\n")
            time.sleep(1)

    def stop(self):
        self.running = False

    def update_temperature_range(self):
        """ Dynamically update temperature range based on the current climate """
        global climate
        if climate == "winter":
            self.min_temp = -10.0
            self.max_temp = -8.0
        elif climate == "spring":
            self.min_temp = 25.0
            self.max_temp = 27.0
        else:  # summer
            self.min_temp = 30.0
            self.max_temp = 33.0


def main():
    no_of_partitions = 7
    no_of_sensors_in_each_part = [3, 4, 5, 6, 7, 8, 9]
    allSensors = []


    climate_thread = threading.Thread(target=change_climate)
    climate_thread.daemon = True
    climate_thread.start()


    for j in range(no_of_partitions):
        allSensors.append([])

        for i in range(no_of_sensors_in_each_part[j]):
            sensor = TemperatureSensor(sensor_id=f"ID ({j},{i})")
            allSensors[j].append(sensor)
            sensor.start()


    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    main()
