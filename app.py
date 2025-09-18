from flask import Flask, Response
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

app = Flask(__name__)

# 📷 Camera setup
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24
raw_capture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)  # allow camera to warm up

def generate_frames():
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        image = frame.array
        ret, buffer = cv2.imencode('.jpg', image)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        raw_capture.truncate(0)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return """
    <html>
    <head><title>Raspberry Pi Camera</title></head>
    <body>
    <h1>Raspberry Pi Camera Streaming</h1>
    <img src="/video_feed" width="640" height="480">
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
