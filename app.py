from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, join_room, emit
import csv
import threading
import time
import cv2
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

def get_data(date):
    path = os.path.expanduser('~')+ "/data/"
    print(date)
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
    print("data ready")

def generate_frames():
    # Ouvrir le flux RTSP avec OpenCV
    cap = cv2.VideoCapture('rtsp://root:pendule2023@192.168.125.206:554/axis-media/media.amp')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir l'image en format JPEG pour la diffusion
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Diffuser l'image en tant que flux vidéo
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Libérer les ressources après la fin de la diffusion
    cap.release()


def read_data():
    path = os.path.expanduser('~')+ "/data/"
    files = os.listdir(path)
    global dates
    dates = []
    for file in files:
        dates.append(file.split("-", 1)[1])
    dates.sort()
    print(dates)
    get_data(dates[-1])
    while True:
        with open(path + 'pFposition-' + dates[-1], 'r') as file:
            lines = file.readlines()
            last_line = lines[-1]
            t = last_line[0:9]
            x = last_line[9:13]
            y = last_line[13:18]

@socketio.on('connect')
def handle_connect():
    room_id = request.sid  # Utilisez l'ID de session comme identifiant de la chambre
    join_room(room_id)
    emit('metaData', {'dataLength': len(data)}, room=room_id)

@socketio.on('get_data')
def handle_get_data(dataIndex):
    room_id = request.sid
    emit('data', data[int(dataIndex["time"]):int(dataIndex["time"]) + int(dataIndex["points"])], room=room_id)

@socketio.on('change_date')
def handle_change_date(date):
    room_id = request.sid
    get_data(date["date"])
    emit('metaData', {'dataLength': len(data)}, room=room_id)

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
    return render_template('mesures.html', dates=dates)

@app.route('/camera')
def camera():
    return render_template('camera.html', video_feed='/video_feed')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    thread = threading.Thread(target=read_data)
    thread.start()
    socketio.run(app, host='0.0.0.0')
