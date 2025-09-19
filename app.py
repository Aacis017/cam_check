from flask import Flask, Response, render_template
from picamera2 import Picamera2
from libcamera import Transform
import cv2
import threading

app = Flask(__name__)

# Initialize camera with 180° rotation
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480)},
    transform=Transform(hflip=1, vflip=1)  # 180° rotation
)
picam2.configure(config)
picam2.start()

# Shared frame
frame = None
lock = threading.Lock()

def update_frame():
    global frame
    while True:
        img = picam2.capture_array()
        ret, jpeg = cv2.imencode('.jpg', img)
        if ret:
            with lock:
                frame = jpeg.tobytes()

# Start background thread
threading.Thread(target=update_frame, daemon=True).start()

def generate_frames():
    global frame
    while True:
        if frame:
            with lock:
                f = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + f + b'\r\n')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
