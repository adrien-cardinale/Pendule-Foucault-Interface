from flask import Flask, render_template
from flask_socketio import SocketIO
import csv
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)


def get_data():
    print("get_data")
    with open('data.csv', 'r') as file:
        lines = file.readlines()
        global data
        data = []
        for i in range(0, len(lines), 4):
            if lines[i] == '\n':
                continue
            x = lines[i].split(',')[0]
            y = lines[i].split(',')[1]
            timestamp = lines[i].split(',')[2].split(".")[0]
            data.append({'x': x, 'y': y, 'timestamp': timestamp})
    print("data ready")
    

@socketio.on('connect')
def handle_connect():
    socketio.emit('metaData', {'dataLength': len(data)})


@socketio.on('get_data')
def handle_get_data(dataIndex):
    socketio.emit('data', data[int(dataIndex["time"]):int(dataIndex["time"]) + int(dataIndex["points"])])

@socketio.on('get_labels')
def handle_get_labels():
    labels = {"minTime": data[0]['timestamp'], "maxTime": data[-1]['timestamp']}
    socketio.emit('labels', labels)



@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    get_data()
    socketio.run(app, debug=True)
