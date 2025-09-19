from flask import Flask, Response, render_template_string
from picamera2 import Picamera2
import io

app = Flask(__name__)

# Init camera
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# HTML Page
html = """
<!DOCTYPE html>
<html>
<head><title>Pi Camera Stream</title></head>
<body>
  <h1>📷 Raspberry Pi Zero 2W Camera Stream</h1>
  <img src="{{ url_for('video_feed') }}" width="640" height="480">
</body>
</html>
"""

def generate_frames():
    while True:
        buf = io.BytesIO()
        # Capture JPEG directly into buffer
        picam2.capture_file(buf, format='jpeg')
        frame = buf.getvalue()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
