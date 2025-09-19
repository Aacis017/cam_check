from flask import Flask, Response, render_template
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from libcamera import Transform
import io

app = Flask(__name__)

# Initialize camera with 180° rotation
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (320, 240)},  # smaller resolution for faster Pi Zero
    transform=Transform(hflip=1, vflip=1)
)
picam2.configure(config)
picam2.start()

def generate_frames():
    while True:
        stream = io.BytesIO()
        picam2.capture_file(stream, format="jpeg")  # fast JPEG capture
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + stream.getvalue() + b'\r\n')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
