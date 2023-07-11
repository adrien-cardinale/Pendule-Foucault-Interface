from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, join_room, emit
import csv
import threading
import time
import cv2
from datetime import datetime
import os
import eventlet
import numpy as np
from flask_cors import CORS
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

xCenter = 1203
yCenter = 1357

path = os.path.expanduser('~') + "/data/"


def get_data(date):
    with open(path + 'pFposition-' + date, 'r') as file:
        lines = file.readlines()
        global data
        data = []
        for i in range(0, len(lines), 4):
            if lines[i] == '\n':
                continue
            t = lines[i][0:9]
            x = lines[i][9:13]
            y = lines[i][13:18]
            data.append({'x': x, 'y': y, 'timestamp': t})


def get_driver_data(date):
    global data_moteur
    data_moteur = []
    with open(path + 'pFregulateur-' + date, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 4):
            t = lines[i].split(",")[0]
            I = lines[i].split(",")[1]
            p = lines[i].split(",")[2][:-1]
            data_moteur.append({'I': I, 'p': p, 'timestamp': t})


def get_date():
    files = os.listdir(path)
    global dates
    dates = []
    for file in files:
        if file.startswith("pFposition-"):
            dates.append(file.split("-", 1)[1])
    dates.sort()


def read_data():
    get_data(dates[-1])
    get_driver_data(dates[-1])
    amplitude = 0
    while True:
        x = []
        y = []
        for i in range(0, 400):
            with open(path + 'pFposition-' + dates[-1], 'r') as file:
                lines = file.readlines()
                last_line = lines[-1]
                _t = last_line[0:9]
                _x = last_line[9:13]
                _y = last_line[13:17]
                socketio.emit('data2', [{'x': _x, 'y': _y, 'timestamp': _t}])
                x.append(int(_x))
                y.append(int(_y))
            time.sleep(0.05)
            socketio.emit('amplitude', {'amplitude': amplitude})
        amplitude = int(np.sqrt((np.max(x)-xCenter) ** 2 + (np.max(y)-yCenter) ** 2))


@socketio.on('connect')
def handle_connect():
    room_id = request.sid
    join_room(room_id)
    emit('metaData', {'dataLength': len(data)}, room=room_id)
    emit('metaData_moteur', {'dataLength': len(data_moteur)}, room=room_id)


@socketio.on('get_data')
def handle_get_data(dataIndex):
    room_id = request.sid
    emit('data', data[int(dataIndex["time"]):int(dataIndex["time"]) + int(dataIndex["points"])], room=room_id)


@socketio.on('change_date')
def handle_change_date(date):
    room_id = request.sid
    get_data(date["date"])
    emit('metaData', {'dataLength': len(data)}, room=room_id)


@socketio.on('get_data_moteur')
def handle_get_data_moteur(dataIndex):
    room_id = request.sid
    emit('data_moteur', data_moteur[int(dataIndex["time"]):int(dataIndex["time"]) + int(dataIndex["points"])], room=room_id)


@socketio.on('change_date_moteur')
def handle_change_date_moteur(date):
    room_id = request.sid
    get_driver_data(date["date"])
    emit('metaData_moteur', {'dataLength': len(data_moteur)}, room=room_id)


@socketio.on('get_labels')
def handle_get_labels():
    room_id = request.sid
    labels = {"minTime": data[0]['timestamp'], "maxTime": data[-1]['timestamp']}
    emit('labels', labels, room=room_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mesures')
def mesures():
    get_date()
    return render_template('mesures.html', dates=dates)


@app.route('/moteur')
def moteur():
    return render_template('moteur.html', dates=dates)


@app.route('/camera')
def camera():
    return render_template('camera.html')


if __name__ == '__main__':
    get_date()
    eventlet.monkey_patch()
    eventlet.spawn(read_data)
    # eventlet.spawn(generate_frames)
    socketio.run(app, host='0.0.0.0', port=8080)
