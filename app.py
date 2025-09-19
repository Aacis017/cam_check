from flask import Flask, Response, render_template
from picamera2 import Picamera2
from libcamera import Transform
import io

app = Flask(__name__)

# Initialize Picamera2
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(transform=Transform(hflip=True), queue=False)
picam2.configure(preview_config)
picam2.start()

def generate_frames():
    while True:
        # Capture a frame as JPEG
        frame = picam2.capture_array()
        from PIL import Image
        import numpy as np

        # Convert to JPEG in memory
        img = Image.fromarray(frame)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        jpeg = buf.getvalue()

        # Yield as MJPEG frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
