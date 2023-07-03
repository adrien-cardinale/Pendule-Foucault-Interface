from flask import Flask, render_template
from flask_socketio import SocketIO
import csv
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)


def get_data():
    with open('oscillation4.csv', 'r') as file:
        lines = file.readlines()
        global data
        data = []
        for i in range(0, len(lines), 10):
            x = lines[i].split(',')[0]
            y = lines[i].split(',')[1]
            timestamp = lines[i].split(',')[2]
            data.append({'x': x, 'y': y, 'timestamp': timestamp})
    

@socketio.on('connect')
def handle_connect():
    socketio.emit('data', data)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    get_data()
    socketio.run(app, debug=True)
