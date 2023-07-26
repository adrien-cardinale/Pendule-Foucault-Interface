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
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

path = os.path.expanduser('~') + "/data/"



def load_config():
    global positionDateLoaded
    positionDateLoaded = ""
    global moteurDateLoaded
    moteurDateLoaded = ""
    global xCenter
    global yCenter
    global periode
    with open(path + 'configPF.json') as json_file:
        data = json.load(json_file)
        xCenter = data['center']['x']
        yCenter = data['center']['y']
        periode = data['periode']


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
            timeMs = int(lines[i][0:2]) * 3600000 + int(lines[i][2:4]) * 60000 + int(lines[i][4:6]) * 1000 + int(lines[i][6:9])
            data.append({'x': x, 'y': y, 'timestamp': t, 'timeMs': timeMs})


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
                if last_line == '\n':
                    continue
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


@socketio.on('get_data_position')
def handle_get_data(message):
    global periode
    global positionDateLoaded
    room_id = request.sid
    if message["date"] == "":
        date = dates[-1]
    else:
        date = message["date"]
    if positionDateLoaded != date:
        get_data(date)
        positionDateLoaded = date
    emit('data', data[int(message["index"]):int(message["index"])+300], room=room_id)


@socketio.on('get_data_moteur')
def handle_get_data_moteur(message):
    room_id = request.sid
    global moteurDateLoaded
    if message["date"] == "":
        date = dates[-1]
    else:
        date = message["date"]
    if moteurDateLoaded != date:
        get_data(date)
        moteurDateLoaded = date
    emit('data_moteur', data_moteur[int(message["index"]):int(message["index"])+300], room=room_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/position')
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
    load_config()
    get_date()
    eventlet.monkey_patch()
    eventlet.spawn(read_data)
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
