class Config:
    SECRET_KEY = "dbdd91de1ea616b24740a3d963a7f95c"

    MONGO_URI = "mongodb://localhost:27017/"

    # MQTT configuration
    MQTT_BROKER_URL = "test.mosquitto.org"
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = ""
    MQTT_PASSWORD = ""
    MQTT_KEEPALIVE = 5
    MQTT_TLS_ENABLED = False
