from flask import Flask, Response, render_template
from picamera2 import Picamera2
from libcamera import Transform
import io
from PIL import Image

app = Flask(__name__)

# Camera setup
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480)},
    transform=Transform(hflip=1, vflip=1),
    queue=False  # always latest frame
)
picam2.configure(config)
picam2.start()

def generate_frames():
    while True:
        frame = picam2.capture_array()  # get numpy array
        img = Image.fromarray(frame)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        jpeg = buf.getvalue()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
