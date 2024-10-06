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
        current_index = (current_index + 1) % len(climates)  
        time.sleep(10)

# Sensor ID for each partition (as coordinate locations)
TempsensorID = [
    ["(3,2)", "(3,2)"],               # Partition 1
    ["(4,9)", "(4,19)", "(4,19)", "(4,9)"],  # Partition 2
    ["(5,28)", "(5,41)", "(5,28)", "(5,41)"], # Partition 3
    ["(6,5)", "(6,2)", "(6,5)", "(6,2)"],     # Partition 4
    ["(4,12)", "(4,19)", "(4,19)", "(4,12)"], # Partition 5
    ["(4,52)", "(4,52)", "(4,46)", "(4,46)"],  # Partition 6
    ["(4,28)", "(4,36)", "(4,28)", "(4,36)"]   # Partition 7
]


climate_temperature_values = {
    "winter": [0.0, -1.0, -1.5, -2.0, -1.8, -2.3, -0.5],  # Winter values
    "spring": [15.0, 16.0, 15.5, 15.8, 16.3, 16.8, 16.1], # Spring values
    "summer": [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]  # Summer values
}

class TemperatureSensor(threading.Thread):
    def __init__(self, sensor_id, partition_id):
        threading.Thread.__init__(self)
        self.sensor_id = sensor_id
        self.partition_id = partition_id
        self.running = True
        self.update_temperature_range() 

    def run(self):
        while self.running:
            temperature = self.get_temperature_value()
            print(f"\nSensor {self.sensor_id}: {temperature:.2f}°C")
            time.sleep(1)

    def stop(self):
        self.running = False

    def update_temperature_range(self):
        """ Update the temperature values based on the current climate """
        global climate
        self.temperature_values = climate_temperature_values[climate]

    def get_temperature_value(self):
        """ Get a temperature value close to the current climate values, with slight variation """
        # Choose a base temperature from the current climate's values
        base_temperature = random.choice(self.temperature_values)
        # Add a small random value between -0.1 and 0.1
        variation = random.uniform(-0.1, 0.1)
        return base_temperature + variation

def main():
    no_of_partitions = len(TempsensorID)
    allSensors = []

    
    climate_thread = threading.Thread(target=change_climate)
    climate_thread.daemon = True
    climate_thread.start()

    
    for j in range(no_of_partitions):
        allSensors.append([])
        for coord in TempsensorID[j]:
            sensor = TemperatureSensor(sensor_id=coord, partition_id=j)  # Pass partition ID
            allSensors[j].append(sensor)
            sensor.start()

    try:
        while True:
            time.sleep(0.1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("\nStopping all sensors...\n")
        for partition in allSensors:
            for sensor in partition:
                sensor.stop()  
                sensor.join()  
        print("All sensors stopped.")

if __name__ == "__main__":
    main()
