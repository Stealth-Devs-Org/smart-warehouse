from flask_socketio import SocketIO, emit

socketio = SocketIO()


@socketio.on("connected")
def handle_my_custom_event(json):
    print("received json: " + str(json))
