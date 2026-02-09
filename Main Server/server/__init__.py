from flask import Flask

from server.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    from server.mqtt.utils import ConnectMQTT, mqtt_client

    # mqtt_client.init_app(app)
    ConnectMQTT()

    from server.agv.col_avoid import agv

    app.register_blueprint(agv)

    from server.websocket.utils import socketio

    socketio.init_app(app)

    return app
