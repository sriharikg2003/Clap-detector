# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading
from physics import TapTester

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def background_thread():
    tt = TapTester(socketio)
    timer_start_time = time.time()

    while not tt.clap_detected and time.time() - tt.start_time <= 6:
        now = time.time()
        timer_value = int(now - timer_start_time)
        socketio.emit('timer', {'timer_value': timer_value})
        tt.listen(now)
    
    # Ensure the last result is sent when the loop exits
    elapsed_time = int(time.time() - timer_start_time)
    tap_message = f"Tapped at time: {elapsed_time} seconds"
    result_message = "WIN" if 4 <= elapsed_time < 5 else "LOST"

    tt.stop()
    tt.clap_detected = True
    tt.socketio.emit('result', {'message': result_message, 'tap_message': tap_message})


@socketio.on('connect')
def handle_connect():
    emit('timer', {'timer_value': 0})
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
