import threading
import os
import time
import sys
import paho.mqtt.client as mqtt
from actuatorUtils import SetActuatorState, actuator_state, ReadVariableFromDatabase

sys.path.append('Virtual Sensor Actuator')
from warehouseEnvironment import desired_warehouse_airquality_values


AirQualityCtrlID = [
    # Partition 1
    ["(2,2)"],
    
    # Partition 2
    ["(9,11)"],
    
    # Partition 3
    ["(28,11)"],
    
    # Partition 4
    ["(5,15)"],
    
    # Partition 5
    ["(12,27)"],
    
    # Partition 6
    ["(52,13)"],
    
    # Partition 7
    ["(28,18)"]
]

BROKER = "localhost"  
PORT = 1883
TOPIC = "/actuator_AirQuality"

class AirQualityCtrl(threading.Thread):
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
        self.connect_mqtt()
        while self.running:
            rateofChange = self.get_RateofChange()
            self.AdjustValues(rateofChange, "AirQuality Values")
            SetActuatorState("AirQualityController", self.actuator_id,  self.partition_id, self.actuator_id, round(rateofChange, 2), 1)
            print(f"Actuator state: {actuator_state}")
            self.client.publish(TOPIC, str(actuator_state)) 
            time.sleep(1.2)

    def stop(self):
        self.running = False
        self.client.loop_stop()

    # def get_airquality_value(self):
    #     global warehouse_airquality_values
    #     base_temperature = warehouse_airquality_values[self.partition_id]
    #     variation = random.uniform(-0.1, 0.1)
    #     return base_temperature + variation



    def get_RateofChange(self):  # optional to send in Mqtt
        rateofchange = 5
        return rateofchange

    def AdjustValues(self,rateOfChange, variable):
        warehouse_airquality_values = ReadVariableFromDatabase("AirQuality Values")
        global desired_warehouse_airquality_values


        if desired_warehouse_airquality_values[self.partition_id] - warehouse_airquality_values[self.partition_id] < rateOfChange and desired_warehouse_airquality_values[self.partition_id] - warehouse_airquality_values[self.partition_id] > 0:
            warehouse_airquality_values[self.partition_id] = desired_warehouse_airquality_values[self.partition_id]
            self.writeValuesToDatabase(warehouse_airquality_values, variable)

        elif desired_warehouse_airquality_values[self.partition_id] > warehouse_airquality_values[self.partition_id]:
            value = warehouse_airquality_values[self.partition_id] + rateOfChange
            warehouse_airquality_values[self.partition_id] = round(value, 1)

            self.writeValuesToDatabase(warehouse_airquality_values, variable)
        
        elif desired_warehouse_airquality_values[self.partition_id] < warehouse_airquality_values[self.partition_id]:
            value = warehouse_airquality_values[self.partition_id] - rateOfChange
            warehouse_airquality_values[self.partition_id] = round(value, 1)
            self.writeValuesToDatabase(warehouse_airquality_values, variable)

    

    def writeValuesToDatabase(self,values,variable):
        directory = 'Virtual Sensor Actuator'
        filename = 'warehouse_Env_data.txt'
        filepath = os.path.join(directory, filename)
        
        warehouse_temperature_values = ReadVariableFromDatabase("Temperature Values")
        warehouse_airquality_values = ReadVariableFromDatabase("AirQuality Values")
        warehouse_smoke_values = ReadVariableFromDatabase("Smoke Values")
        warehouse_humidity_values = ReadVariableFromDatabase("Humidity Values")

        if variable == "Temperature Values":
            warehouse_temperature_values = values 
        elif variable == "AirQuality Values":
            warehouse_airquality_values = int(values)
        elif variable == "Smoke Values":
            warehouse_smoke_values = values
        elif variable == "Humidity Values":
            warehouse_humidity_values = values
        


        with open(filepath, 'w') as file:
            file.write("Temperature Values :\n")
            file.write(', '.join(map(str, warehouse_temperature_values)) + "\n\n")
            
            file.write("AirQuality Values :\n")
            file.write(', '.join(map(str, warehouse_airquality_values)) + "\n\n")
            
            file.write("Smoke Values :\n")
            file.write(', '.join(map(str, warehouse_smoke_values)) + "\n\n")
            
            file.write("Humidity Values :\n")
            file.write(', '.join(map(str, warehouse_humidity_values)) + "\n")


            


def main():
    no_of_partitions = len(AirQualityCtrlID)
    allActuators = []

    for j in range(no_of_partitions):
        allActuators.append([])
        for coord in AirQualityCtrlID[j]:
            actuator = AirQualityCtrl(actuator_id=coord, partition_id=j)  
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
