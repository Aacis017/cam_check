from flask import Flask, Response, render_template
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from libcamera import Transform
import io

app = Flask(__name__)

# Camera setup with rotation
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480)},
    transform=Transform(hflip=1, vflip=1)  # rotate 180°
)
picam2.configure(config)

# Use an in-memory buffer
stream = io.BytesIO()
output = FileOutput(stream)
encoder = MJPEGEncoder()

# Start streaming
picam2.start_recording(encoder, output)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            data = stream.getvalue()
            if data:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
                stream.seek(0)
                stream.truncate()
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
