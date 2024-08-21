from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from server.config import Config


db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from server.mqtt.utils import mqtt_client
    mqtt_client.init_app(app)
    
    return app