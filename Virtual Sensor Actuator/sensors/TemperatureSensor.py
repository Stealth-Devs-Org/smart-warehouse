import threading
import random
import time


from sensorUtils import SetSensorState, sensor_state



#sensor_state = {"sensor_type": "", "sensor_id": "", "sensor_location": "", "reading": 0.0, "current_status": 0}

# def SetSensorState(type, id, location, reading, status):
#     global sensor_state
#     sensor_state["sensor_type"] = type
#     sensor_state["sensor_id"] = id
#     sensor_state["sensor_location"] = location
#     sensor_state["reading"] = reading
#     sensor_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)
#     #print(f"Received new sensor state: {sensor_state}")

    
climate = "winter"

def change_climate():
    global climate
    climates = ['winter', 'spring', 'summer']
    current_index = 0
    while True:
        climate = climates[current_index]
        #print(f"\nClimate changed to: {climate}\n")  
        current_index = (current_index + 1) % len(climates)  
        time.sleep(5)

climate_temperature_values = {
    "winter": [0.0, -1.0, -1.5, -2.0, -1.8, -2.3, -0.5],  # Winter values with 7 partitions
    "spring": [15.0, 16.0, 15.5, 15.8, 16.3, 16.8, 16.1], # Spring values with 7 partitions
    "summer": [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]  # Summer values with 7 partitions
}

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
        self.last_climate = climate  
        self.update_temperature_range()
        

    def run(self):
        while self.running:
            if self.last_climate != climate:
                self.update_temperature_range()
                self.last_climate = climate  
            temperature = self.get_temperature_value()
            print(f"\nSensor {self.sensor_id}: {temperature:.2f}°C")
            SetSensorState("Temperature", self.sensor_id, self.sensor_id, temperature, 1)
            print(f"Sensor state: {sensor_state}")
            time.sleep(1)

    def stop(self):
        self.running = False

    def update_temperature_range(self):
        """ Update the temperature values based on the current climate """
        global climate
        self.temperature_values = climate_temperature_values[climate]

    def get_temperature_value(self):
        """ Get a temperature value close to the current climate values, with slight variation """
        base_temperature = self.temperature_values[self.partition_id]
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
            time.sleep(0.1)  
    except KeyboardInterrupt:
        print("\nStopping all sensors...\n")
        for partition in allSensors:
            for sensor in partition:
                sensor.stop()  
                sensor.join()  
        print("All sensors stopped.")

if __name__ == "__main__":
    main()
