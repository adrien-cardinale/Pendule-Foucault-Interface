from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit
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
    room_id = request.sid  # Utilisez l'ID de session comme identifiant de la chambre
    join_room(room_id)
    emit('metaData', {'dataLength': len(data)}, room=room_id)

@socketio.on('get_data')
def handle_get_data(dataIndex):
    room_id = request.sid
    emit('data', data[int(dataIndex["time"]):int(dataIndex["time"]) + int(dataIndex["points"])], room=room_id)

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
    return render_template('mesures.html')

if __name__ == '__main__':
    get_data()
    socketio.run(app, debug=True, host='0.0.0.0')
