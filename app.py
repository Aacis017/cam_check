from flask import Flask, Response, render_template
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import CircularOutput
from libcamera import Transform

app = Flask(__name__)

# Camera setup
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480)},
    transform=Transform(hflip=1, vflip=1)  # rotate 180°
)
picam2.configure(config)

# Use CircularOutput for streaming (no recording)
stream = CircularOutput(capacity=1024*1024)  # 1MB buffer
encoder = MJPEGEncoder()
picam2.start_recording(encoder, stream)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    def generate():
        last_pos = 0
        while True:
            data = stream.read()
            if data:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
