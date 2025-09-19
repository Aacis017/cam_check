from flask import Flask, Response,render_template
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import io

app = Flask(__name__)

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))

# Set up in-memory MJPEG output
stream = io.BytesIO()
encoder = MJPEGEncoder()
output = FileOutput(stream)
picam2.start_encoder(encoder, output)

def generate_frames():
    while True:
        stream.seek(0)
        frame = stream.read()
        if frame:
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        stream.seek(0)
        stream.truncate()
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template("index.html")
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
