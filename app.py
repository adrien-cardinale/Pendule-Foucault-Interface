from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, join_room, emit
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import time
import os
import eventlet
import numpy as np
import json
import socket
from datetime import datetime, timedelta
import gzip
import shutil
from io import BytesIO
from zipfile import ZipFile

TCP_IP = '192.168.125.208'
TCP_PORT = 2091
BUFFER_SIZE = 1024

app = Flask(__name__)
socketio = SocketIO(app)
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("pendule2023")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
    

path = os.path.expanduser('~') + "/data/"
pathArchive = os.path.expanduser('~') + "/archive/"

global amplitude
amplitude = 0


def load_config():
    global positionDateLoaded
    positionDateLoaded = ""
    global moteurDateLoaded
    moteurDateLoaded = ""
    global xCenter
    global yCenter
    global periode
    with open(path + 'configPF.json', 'r') as json_file:
        data = json.load(json_file)
        try:
            xCenter = float(data['center']['x'])
            yCenter = float(data['center']['y'])
            periode = float(data['periode'])
        except:
            print("Error loading config file")


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
            try:
                timeMs = int(lines[i][0:2]) * 3600000 + int(lines[i][2:4]) * 60000 + int(lines[i][4:6]) * 1000 + int(lines[i][6:9])
                data.append({'x': x, 'y': y, 'timestamp': t, 'timeMs': timeMs})
            except:
                print(f"Error loading data {i}")


def get_driver_data(date):
    global data_moteur
    data_moteur = []
    with open(path + 'pFregulateur-' + date, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 2):
            t = lines[i].split(",")[0]
            I = lines[i].split(",")[1]
            p = lines[i].split(",")[2][:-1]
            timeMs = int(lines[i][0:2]) * 3600000 + int(lines[i][2:4]) * 60000 + int(lines[i][4:6]) * 1000 + int(lines[i][6:9])
            data_moteur.append({'I': I, 'p': p, 'timestamp': t, "timeMs": timeMs})


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
    global amplitude
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


def get_status():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_IP, TCP_PORT))
            s.send("GET".encode())
            s.settimeout(1)
            data = s.recv(BUFFER_SIZE)
            s.close()
            time.sleep(1)
            socketio.emit('status', {'status': data.decode()})
        except:
            print("erreur lors de la récupération du status")
    


@socketio.on('connect')
def handle_connect():
    global amplitude
    room_id = request.sid
    join_room(room_id)
    emit('metaData', {'dataLength': len(data)}, room=room_id)
    emit('metaData_moteur', {'dataLength': len(data_moteur)}, room=room_id)
    socketio.emit('amplitude', {'amplitude': amplitude})


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


@socketio.on('change_date')
def handle_change_date(message):
    get_data(message)
    emit('metaData', {'dataLength': len(data)}, room=request.sid)


@socketio.on('get_data_moteur')
def handle_get_data_moteur(message):
    room_id = request.sid
    global moteurDateLoaded
    if message["date"] == "":
        date = dates[-1]
    else:
        date = message["date"]
    if moteurDateLoaded != date:
        get_driver_data(date)
        moteurDateLoaded = date
    emit('data_moteur', data_moteur[int(message["index"]):int(message["index"])+60], room=room_id)


@socketio.on('change_date_moteur')
def handle_change_date_moteur(message):
    get_driver_data(message)
    emit('metaData_moteur', {'dataLength': len(data_moteur)}, room=request.sid)


@socketio.on('startExcitation')
def handle_start_excitation():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send("RUN".encode())
    s.close()


@socketio.on('stopExcitation')
def handle_stop_excitation():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send("STOP".encode())
    s.close()


@socketio.on('getConfig')
def handle_get_config():
    with open(path + 'configPF.json') as json_file:
        data = json.load(json_file)
        emit('config', data)


@socketio.on('reloadConfig')
def handle_reload_config(message):
    with open(path + 'configPF.json', 'r') as json_file:
        data = json.load(json_file)
    data['center']['x'] = message['centerX']
    data['center']['y'] = message['centerY']
    data['periode'] = message['periode']
    data['nominalAmplitude'] = message['nominalAmplitude']
    data['excitationAmplitude'] = message['excitationAmplitude']
    data['detectionRadius'] = message['detectionRadius']
    data['startPosition'] = message['startPosition']
    data['KpAmplitude'] = message['KpAmplitude']
    data['offsetDetection'] = message['offsetDetection']
    with open(path + 'configPF.json', 'w') as json_file:
        json.dump(data, json_file)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send("RELOAD".encode())
    s.close()


@socketio.on('getHistorique')
def handle_get_historique(message):
    startDate = message['startDate']
    endDate = message['endDate']
    start_date = datetime.strptime(startDate, '%Y-%m-%d')
    end_date = datetime.strptime(endDate, '%Y-%m-%d')
    dateList = []
    while start_date <= end_date:
        dateList.append(start_date.strftime('%Y-%m-%d'))
        start_date += timedelta(days=1)
    datesPosition = []
    datesRegulateur = []
    for date in dateList:
        if os.path.isfile(pathArchive + 'pFposition-' + date + '.gz'):
            datesPosition.append(date)
        if os.path.isfile(pathArchive + 'pFregulateur-' + date + '.gz'):
            datesRegulateur.append(date)
    emit('historique', {'datesPosition': datesPosition, 'datesRegulateur': datesRegulateur})



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/position')
def mesures():
    get_date()
    return render_template('mesures.html', dates=dates)


@app.route('/moteur')
def moteur():
    get_date()
    return render_template('moteur.html', dates=dates)


@app.route('/camera')
def camera():
    return render_template('camera.html')


@app.route('/historique')
def historique():
    return render_template('historique.html')


@app.route('/config')
@auth.login_required
def config():
    return render_template('config.html')


@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    ## uncompress files .gz pfposition and pfregulateur and add them to an zip archive to download without saving it on the server
    streamPosition = BytesIO()
    streamRegulateur = BytesIO()
    with gzip.open(pathArchive + 'pFposition-' + filename + '.gz', 'rb') as f:
        shutil.copyfileobj(f, streamPosition)
    with gzip.open(pathArchive + 'pFregulateur-' + filename + '.gz', 'rb') as f:
        shutil.copyfileobj(f, streamRegulateur)
    streamPosition.seek(0)
    streamRegulateur.seek(0)
    stream = BytesIO()
    with ZipFile(stream, 'w') as zip:
        zip.writestr('pFposition-' + filename, streamPosition.getvalue())
        zip.writestr('pFregulateur-' + filename, streamRegulateur.getvalue())
    stream.seek(0)

    return send_file(stream, as_attachment=True, download_name="pF-" + filename + ".zip")



if __name__ == '__main__':
    load_config()
    get_date()
    eventlet.monkey_patch()
    eventlet.spawn(read_data)
    eventlet.spawn(get_status)
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
