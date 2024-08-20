from flask import Flask, jsonify
from flask_mqtt import Mqtt
from flask_sqlalchemy import SQLAlchemy
from server.config import Config

db = SQLAlchemy()
mqtt_client = Mqtt()


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
    else:
        print('Bad connection. Code:', rc)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    mqtt_client.init_app(app)
    
    return app