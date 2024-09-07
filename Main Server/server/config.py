import os

import dotenv


class Config:

    project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
    dotenv_path = os.path.join(project_dir, ".env")
    dotenv.load_dotenv(dotenv_path)

    SECRET_KEY = os.getenv("SECRET_KEY")

    MONGO_URI = os.getenv("MONGO_URI")

    # MQTT configuration
    MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL")
    MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT"))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
    MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE"))
    MQTT_TLS_ENABLED = os.getenv("MQTT_TLS_ENABLED", "false").lower() in ("true", "1", "yes")
