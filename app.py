from flask import Flask, Response, render_template
from picamera2 import Picamera2, MJPEGEncoder
from libcamera import Transform

app = Flask(__name__)

# Init camera with 180° rotation
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480)},
    transform=Transform(hflip=1, vflip=1)  # rotate 180°
)
picam2.configure(config)
picam2.start()

# Start MJPEG encoder
encoder = MJPEGEncoder()
picam2.start_recording(encoder, "stream.mjpeg")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(open("stream.mjpeg", "rb"),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
