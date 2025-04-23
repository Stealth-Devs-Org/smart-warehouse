import json
import threading



with open("server/agv/json_data/agv_data.json", "w") as f:
    json.dump({}, f)

with open("server/agv/json_data/sent_interrupts.json", "w") as f:
    json.dump({}, f)

with open("server/agv/json_data/permanent_obstacles.json", "w") as f:
    json.dump({}, f)

with open("server/agv/json_data/working_agvs.json", "w") as f:
    json.dump({}, f)

with open("server/agv/json_data/collisions.json", "w") as f:
    json.dump([], f)

from server import create_app
#from server.agv.col_avoid import run_collision_avoidance
from server.agv.keep_alive import remove_timeout_agvs, start_saving_data_thread
from server.agv.scheduler import run_task_scheduler
from server.websocket.utils import socketio, start_emission_thread




# #For Sensor Data
from server.sensors.sensorhandler import send_sensor_data_websocket
from server.actuatorControl.Temperature_ActuatorController import start_temp_actuator_thread 
from server.actuatorControl.Humidity_ActuatorController import start_humidity_actuator_thread
from server.actuatorControl.AirQuality_ActuatorController import start_air_quality_actuator_thread 
from server.actuatorControl.Smoke_ActuatorController import start_smoke_actuator_thread




app = create_app()

if __name__ == "__main__":
    run_task_scheduler(5)  # Run the task scheduler every {arg} seconds
    # run_collision_avoidance(0.25)  # Run the collision avoidance every {arg} second
    remove_timeout_agvs()  # Run the thread to remove timed out AGVs
    start_saving_data_thread(0.25)  # Run the thread to save AGV data
    start_emission_thread(0.5)
    

    #For ActuatorControl Data
    start_temp_actuator_thread()
    start_humidity_actuator_thread()
    start_air_quality_actuator_thread()
    start_smoke_actuator_thread()
    


    socketio.run(app, host="0.0.0.0", port=5000)
