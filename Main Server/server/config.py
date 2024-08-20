
class Config :
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    
    # MQTT configuration
    MQTT_BROKER_URL = "test.mosquitto.org"
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = ''
    MQTT_PASSWORD = ''
    MQTT_KEEPALIVE = 5
    MQTT_TLS_ENABLED = False
    
