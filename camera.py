# import the necessary packages
from flask import Response, Flask, render_template
import threading
import argparse 
import datetime, time
import imutils
import cv2
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
import base64


# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
outputFrame = None
lock = threading.Lock()
 
# initialize a flask object
app = Flask(__name__)
CORS(app, origins=['http://pendule.einet.ad.eivd.ch:8080'])
socketio = SocketIO(app, cors_allowed_origins=["http://pendule.einet.ad.eivd.ch:8080", "http://pendule.einet.ad.eivd.ch:5000"])
 
source = "rtsp://root:pendule2023@192.168.125.206:554/axis-media/media.amp"
cap = cv2.VideoCapture(source)
time.sleep(2.0)

def stream(frameCount):
    global outputFrame, lock
    if cap.isOpened():
        # cv2.namedWindow(('IP camera DEMO'), cv2.WINDOW_AUTOSIZE)
        while True:
            ret_val, frame = cap.read()
            if frame.shape:
                frame = cv2.resize(frame, (640,360))
                with lock:
                    outputFrame = frame.copy()
                frame_data = base64.b64encode(buffer.tobytes()).decode('utf-8')
                socketio.emit('stream', frame.tolist(), namespace='/video')
            else:
                continue 
    else:
        print('camera open failed')

def generate():
    global outputFrame, lock
    while True:
        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue
        # Diffuse le cadre encodé aux clients connectés
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
        socketio.emit('stream', encodedImage.tobytes(), namespace='/video', room='video_room')

@app.route("/")
def video_feed():
    return socketio.send(generate(), namespace='/video')

@socketio.on('connect', namespace='/video')
def on_connect():
    join_room('video_room')

# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=False, default='192.168.2.226',
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=False, default=8000, 
        help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
        help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    t = threading.Thread(target=stream, args=(args["frame_count"],))
    t.daemon = True
    t.start()
 
    # start the flask app
    # app.run(host=args["ip"], port=args["port"], debug=True,
    #     threaded=True, use_reloader=False)
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
 
# release the video stream pointer
cap.release()
cv2.destroyAllWindows()