from flask import Flask
from server.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    
    from server.mqtt.utils import mqtt_client
    mqtt_client.init_app(app)
    
    return app