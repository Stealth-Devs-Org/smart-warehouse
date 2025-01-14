# import json                    #Added by Sai
# import time

# # from flask_mqtt import Mqtt
# import paho.mqtt.client as mqtt

# from server.config import Config 

# from server.websocket.websocket import send_sensor_data_through_websocket


# # create a dictionary to store sensor state all sensor state
# all_Sensor_Temperature_data = {}
# all_Sensor_AirQuality_data = {}
# all_Sensor_Humidity_data = {}



# mqtt_client = mqtt.Client()

# sensor_state = {"sensor_type": "", "sensor_id": "","partition_id": 0, "sensor_location": "", "reading": 0.0, "current_status": 0}

# # def SetSensorState(type, id,partID, location, reading, status):
# #     global sensor_state
# #     sensor_state["sensor_type"] = type
# #     sensor_state["sensor_id"] = id
# #     sensor_state["partition_id"] = partID
# #     sensor_state["sensor_location"] = location
# #     sensor_state["reading"] = reading
# #     sensor_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)

# def ConnectMQTT():
#         mqtt_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
#         mqtt_client.subscribe("/sensor_temperature", qos=1)  
#         print("subscribed to sensor_temperature")
#         mqtt_client.subscribe("/sensor_airquality", qos=1)  
#         print("subscribed to sensor_airquality")
#         mqtt_client.subscribe("/sensor_humidity", qos=1)  
#         print("subscribed to sensor_humidity")
#         mqtt_client.on_message = on_message  
#         mqtt_client.loop_start()  
        


# def on_message(client, userdata, message):
#     topic = message.topic
#     payload = message.payload.decode()
#     #print(f"Received by Server : {topic}: {payload}")

#     # data = {
#     #     "topic": topic,
#     #     "payload": json.loads(payload)   // with toipc and payload
#     #     }
    
#     data = json.loads(payload)

    
    
#     send_sensor_data_through_websocket(data)    #send data to websocket imidiately

#     try:
#         data = json.loads(payload) 
#     except json.JSONDecodeError:
#         print(f"Failed to decode JSON for topic {topic}: {payload}")
#         return

#     # Default values for sensor state
#     sensor_state.update({
#         "sensor_type": "",  # This will be set based on the topic
#         "sensor_id": data.get("sensor_id", "unknown"),
#         "partition_id": data.get("partition_id", 0),
#         "sensor_location": data.get("sensor_location", "unknown"),
#         "reading": 0.0,  # Placeholder, will be updated below
#         "current_status": 0  # Placeholder, will be updated below
#     })

#     if topic == "/sensor_temperature":
#         sensor_state["sensor_type"] = "Temperature"
#         sensor_state["sensor_id"] = data.get("sensor_id")
#         sensor_state["partition_id"] = data.get("partition_id")
#         sensor_state["sensor_location"] = data.get("sensor_location")
#         sensor_state["reading"] = data.get("reading")
#         sensor_state["current_status"] = data.get("current_status")

#         all_Sensor_Temperature_data[sensor_state["location_id"]] = sensor_state["reading"]
        
        



#     elif topic == "/sensor_airquality":
#         sensor_state["sensor_type"] = "AirQuality"
#         sensor_state["sensor_id"] = data.get("sensor_id")
#         sensor_state["partition_id"] = data.get("partition_id")
#         sensor_state["sensor_location"] = data.get("sensor_location")
#         sensor_state["reading"] = data.get("reading")
#         sensor_state["current_status"] = data.get("current_status")

#         all_Sensor_AirQuality_data[sensor_state["location_id"]] = sensor_state["reading"]


        

#     elif topic == "/sensor_humidity":
#         sensor_state["sensor_type"] = "Humidity"
#         sensor_state["sensor_id"] = data.get("sensor_id")
#         sensor_state["partition_id"] = data.get("partition_id")
#         sensor_state["sensor_location"] = data.get("sensor_location")
#         sensor_state["reading"] = data.get("reading")
#         sensor_state["current_status"] = data.get("current_status")

#         all_Sensor_Humidity_data[sensor_state["location_id"]] = sensor_state["reading"]



#     # write all sensor  all data to a file json file
#     with open('all_Sensor_Temperature_data.json', 'w') as json_file:
#         json.dump(all_Sensor_Temperature_data, json_file)
#     with open('all_Sensor_AirQuality_data.json', 'w') as json_file:
#         json.dump(all_Sensor_AirQuality_data, json_file)
#     with open('all_Sensor_Humidity_data.json', 'w') as json_file:
#         json.dump(all_Sensor_Humidity_data, json_file)
    


#     else:
#         print(f"Unknown topic: {topic}")
#         return

  

#     # Print updated sensor state
#     #print(f"Updated sensor state: {sensor_state}")



# import json                    #Added by Sai
# import time

# # from flask_mqtt import Mqtt
# import paho.mqtt.client as mqtt

# from server.config import Config 

# from server.websocket.websocket import send_sensor_data_through_websocket


# # create a dictionary to store sensor state all sensor state
# all_Sensor_Temperature_data = {}
# all_Sensor_AirQuality_data = {}
# all_Sensor_Humidity_data = {}



# mqtt_client = mqtt.Client()

# sensor_state = {"sensor_type": "", "sensor_id": "","partition_id": 0, "sensor_location": "", "reading": 0.0, "current_status": 0}

# # def SetSensorState(type, id,partID, location, reading, status):
# #     global sensor_state
# #     sensor_state["sensor_type"] = type
# #     sensor_state["sensor_id"] = id
# #     sensor_state["partition_id"] = partID
# #     sensor_state["sensor_location"] = location
# #     sensor_state["reading"] = reading
# #     sensor_state["current_status"] = status     # 0 or 1 (0 = inactive, 1 = active)

# def ConnectMQTT():
#         mqtt_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
#         mqtt_client.subscribe("/sensor_temperature", qos=1)  
#         print("subscribed to sensor_temperature")
#         mqtt_client.subscribe("/sensor_airquality", qos=1)  
#         print("subscribed to sensor_airquality")
#         mqtt_client.subscribe("/sensor_humidity", qos=1)  
#         print("subscribed to sensor_humidity")
#         mqtt_client.on_message = on_message  
#         mqtt_client.loop_start()  
        


# def on_message(client, userdata, message):
#     topic = message.topic
#     payload = message.payload.decode()
#     #print(f"Received by Server : {topic}: {payload}")

#     # data = {
#     #     "topic": topic,
#     #     "payload": json.loads(payload)   // with toipc and payload
#     #     }
    
#     data = json.loads(payload)

    
    
#     send_sensor_data_through_websocket(data)    #send data to websocket imidiately

#     try:
#         data = json.loads(payload) 
#     except json.JSONDecodeError:
#         print(f"Failed to decode JSON for topic {topic}: {payload}")
#         return

#     # Default values for sensor state
#     sensor_state.update({
#         "sensor_type": "",  # This will be set based on the topic
#         "sensor_id": data.get("sensor_id", "unknown"),
#         "partition_id": data.get("partition_id", 0),
#         "sensor_location": data.get("sensor_location", "unknown"),
#         "reading": 0.0,  # Placeholder, will be updated below
#         "current_status": 0  # Placeholder, will be updated below
#     })

#     if topic == "/sensor_temperature":
#         sensor_state["sensor_type"] = "Temperature"
#         sensor_state["sensor_id"] = data.get("sensor_id")
#         sensor_state["partition_id"] = data.get("partition_id")
#         sensor_state["sensor_location"] = data.get("sensor_location")
#         sensor_state["reading"] = data.get("reading")
#         sensor_state["current_status"] = data.get("current_status")

        

#     elif topic == "/sensor_airquality":
#         sensor_state["sensor_type"] = "AirQuality"
#         sensor_state["sensor_id"] = data.get("sensor_id")
#         sensor_state["partition_id"] = data.get("partition_id")
#         sensor_state["sensor_location"] = data.get("sensor_location")
#         sensor_state["reading"] = data.get("reading")
#         sensor_state["current_status"] = data.get("current_status")
        

#     elif topic == "/sensor_humidity":
#         sensor_state["sensor_type"] = "Humidity"
#         sensor_state["sensor_id"] = data.get("sensor_id")
#         sensor_state["partition_id"] = data.get("partition_id")
#         sensor_state["sensor_location"] = data.get("sensor_location")
#         sensor_state["reading"] = data.get("reading")
#         sensor_state["current_status"] = data.get("current_status")


#     else:
#         print(f"Unknown topic: {topic}")
#         return

  

#     # Print updated sensor state
#     #print(f"Updated sensor state: {sensor_state}")









# import json
# import time
# import paho.mqtt.client as mqtt

# from server.config import Config
# from server.websocket.websocket import send_sensor_data_through_websocket


# all_Sensor_Temperature_data = {}
# all_Sensor_AirQuality_data = {}
# all_Sensor_Humidity_data = {}

# mqtt_client = mqtt.Client()


# def ConnectMQTT():
#     mqtt_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
#     mqtt_client.subscribe("/sensor_temperature", qos=1)
#     mqtt_client.subscribe("/sensor_airquality", qos=1)
#     mqtt_client.subscribe("/sensor_humidity", qos=1)
#     mqtt_client.on_message = on_message
#     mqtt_client.loop_start()
#     print("MQTT connected and subscribed.")


# def on_message(client, userdata, message):
#     topic = message.topic
#     payload = message.payload.decode()
    
#     try:
#         data = json.loads(payload)
#     except json.JSONDecodeError:
#         print(f"Invalid JSON received on topic {topic}: {payload}")
#         return

#     send_sensor_data_through_websocket(data) 

    
#     if topic == "/sensor_temperature":
#         all_Sensor_Temperature_data[data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
#     elif topic == "/sensor_airquality":
#         all_Sensor_AirQuality_data[data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
#     elif topic == "/sensor_humidity":
#         all_Sensor_Humidity_data[data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
#     else:
#         print(f"Unknown topic: {topic}")
#         return

    
#     write_to_file("all_Sensor_Temperature_data.json", all_Sensor_Temperature_data)
#     write_to_file("all_Sensor_AirQuality_data.json", all_Sensor_AirQuality_data)
#     write_to_file("all_Sensor_Humidity_data.json", all_Sensor_Humidity_data)

#     print(f"Updated data for {topic}: {data}")


# def write_to_file(filename, data):
#     try:
#         with open(filename, 'w') as json_file:
#             json.dump(data, json_file, indent=4)
#     except Exception as e:
#         print(f"Error writing to {filename}: {e}")












import json
import time
import paho.mqtt.client as mqtt
import logging

from server.config import Config
from server.websocket.websocket import send_sensor_data_through_websocket

# Initialize dictionaries for storing sensor data with 7 partitions
all_Sensor_Temperature_data = [{} for _ in range(7)]  # 7 partitions
all_Sensor_AirQuality_data = [{} for _ in range(7)]
all_Sensor_Humidity_data = [{} for _ in range(7)]

mqtt_client = mqtt.Client()


logging.basicConfig(level=logging.INFO)


def ConnectMQTT():
    mqtt_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
    mqtt_client.subscribe("/sensor_temperature", qos=1)
    mqtt_client.subscribe("/sensor_airquality", qos=1)
    mqtt_client.subscribe("/sensor_humidity", qos=1)
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()
    logging.info("MQTT connected and subscribed.")


def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode()

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON received on topic {topic}: {payload}")
        return

    # Send sensor data through WebSocket
    send_sensor_data_through_websocket(data)







    partition_id = data.get("partition_id", -1)
    if partition_id < 0 or partition_id >= 7:
        logging.error(f"Invalid partition_id: {partition_id} in topic {topic}")
        return


    if topic == "/sensor_temperature":
        all_Sensor_Temperature_data[partition_id][data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
    elif topic == "/sensor_airquality":
        all_Sensor_AirQuality_data[partition_id][data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
    elif topic == "/sensor_humidity":
        all_Sensor_Humidity_data[partition_id][data.get("sensor_id", "unknown")] = data.get("reading", 0.0)
    else:
        logging.error(f"Unknown topic: {topic}")
        return


    write_to_file("all_Sensor_Temperature_data.json", all_Sensor_Temperature_data)
    write_to_file("all_Sensor_AirQuality_data.json", all_Sensor_AirQuality_data)
    write_to_file("all_Sensor_Humidity_data.json", all_Sensor_Humidity_data)

    #logging.info(f"Updated data for {topic}: {data}")


def write_to_file(filename, data):
    try:
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        logging.error(f"Error writing to {filename}: {e}")

# Main function to start the script
if __name__ == "__main__":
    ConnectMQTT()
    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        logging.info("MQTT connection stopped.")
