warehouse_temperature_values = [25.0, 25.5, 24.5, 25.5, 23.5, 23.8, 23.7]

partitionNumber = 3
newTempValue = 30

def updateTempValue (partID,value):
    global warehouse_temperature_values
    warehouse_temperature_values[partID-1] = value





if __name__ == "__main__":
    updateTempValue(partitionNumber,newTempValue)
    print(f"Updated temperature value for partition {partitionNumber}: {warehouse_temperature_values[partitionNumber-1]}°C")
