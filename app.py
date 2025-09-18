from flask import Flask, render_template, Response
from picamera2 import Picamera2
import cv2

app = Flask(__name__)

# Setup PiCamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

def generate_frames():
    while True:
        frame = picam2.capture_array()  # Capture frame as numpy array
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
