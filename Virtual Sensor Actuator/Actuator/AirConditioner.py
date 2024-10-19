import threading
import os
import time
import sys
import paho.mqtt.client as mqtt
from actuatorUtils import SetActuatorState, actuator_state, ReadVariableFromDatabase

sys.path.append('Virtual Sensor Actuator')
from warehouseEnvironment import desired_warehouse_airquality_values


AirConditionerID = [
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

BROKER = "localhost"  
PORT = 1883
TOPIC = "/actuator_AirConditioner"

class AirConditioner(threading.Thread):
    def __init__(self, actuator_id, partition_id):
        threading.Thread.__init__(self)
        self.client = mqtt.Client()
        self.actuator_id = actuator_id
        self.partition_id = partition_id
        self.running = True  

    def connect_mqtt(self):
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()  #loop in seperate thread...
        
    def run(self):
        while self.running:
            rateofChange = self.get_RateofChange()
            self.AdjustValues(rateofChange)
            SetActuatorState("AirConditioner", self.actuator_id, self.actuator_id, self.partition_id, round(rateofChange, 2), 1)
            print(f"Actuator state: {actuator_state}")
            self.client.publish(TOPIC, str(actuator_state)) 
            time.sleep(1)

    def stop(self):
        self.running = False
        self.client.loop_stop()

    # def get_temperature_value(self):
    #     global warehouse_temperature_values
    #     base_temperature = warehouse_temperature_values[self.partition_id]
    #     variation = random.uniform(-0.1, 0.1)
    #     return base_temperature + variation


    directory = 'Virtual Sensor Actuator'
    filename = 'warehouse_data.txt'
    filepath = os.path.join(directory, filename)

    def get_RateofChange(self):  # optional to send in Mqtt
        rateofchange = 0.3
        return rateofchange

    def AdjustValues(self,rateOfChange):
        warehouse_temperature_values = ReadVariableFromDatabase("Temperature Values")
        global desired_warehouse_temperature_values

        if desired_warehouse_airquality_values[self.partition_id] > warehouse_temperature_values[self.partition_id]:
            value = warehouse_temperature_values[self.partition_id] + rateOfChange
            warehouse_temperature_values[self.partition_id] = value
            self.writeValuesToDatabase(warehouse_temperature_values)
        
        elif desired_warehouse_airquality_values[self.partition_id] < warehouse_temperature_values[self.partition_id]:
            value = warehouse_temperature_values[self.partition_id] - rateOfChange
            warehouse_temperature_values[self.partition_id] = value
            self.writeValuesToDatabase(warehouse_temperature_values)
        


    def writeValuesToDatabase(values):
        global filepath
        warehouse_temperature_values = values

        with open(filepath, 'w') as file:
            file.write(', '.join(map(str, warehouse_temperature_values)) + "\n\n")
            


def main():
    no_of_partitions = len(AirConditionerID)
    allActuators = []

    for j in range(no_of_partitions):
        allActuators.append([])
        for coord in AirConditionerID[j]:
            actuator = AirConditioner(actuator_id=coord, partition_id=j)  
            allActuators[j].append(actuator) 
            actuator.start()

    try:
        while True:
            time.sleep(1)  
            
    except KeyboardInterrupt:
        print("\nStopping all actuators...")
        for partition in allActuators:
            for actuator in partition:
                actuator.stop()
        for partition in allActuators:
            for actuator in partition:
                actuator.join()
        print("All actuators stopped.")
        

if __name__ == "__main__":
    main()
