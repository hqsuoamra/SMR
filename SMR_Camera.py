import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import numpy as np
import cv2
from adafruit_servokit import ServoKit

PAGE = """\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def remap(x, in_min, in_max, out_min, out_max):
    x_diff = x - in_min
    out_range = out_max - out_min
    in_range = in_max - in_min
    temp_out = x_diff * out_range / in_range + out_min
    if out_max < out_min:
        temp = out_max
        out_max = out_min
        out_min = temp
    if temp_out > out_max:
        return out_max
    elif temp_out < out_min:
        return out_min
    else:
        return temp_out

def main():
    IN_MIN = 30.0
    IN_MAX = 160.0
    OUT_MIN = 160.0
    OUT_MAX = 30.0

    head_angle = 90.0
    head_angle_ave = 90.0
    head_angle_alpha = 0.25

    kit = ServoKit(channels=16)

    cap = cv2.VideoCapture(0)
    cap.set(3, 160)  # set horiz resolution
    cap.set(4, 120)  # set vert res

    object_detector = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=5)

    while True:
        ret, frame = cap.read()
        height, width, _ = frame.shape

        roi = frame[0:240, 0:320]
        mask = object_detector.apply(roi)

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections = []
        biggest_index = 0
        biggest_area = 0
        ind = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 150:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append([x, y, w, h])
                area = w * h
                if area > biggest_area:
                    biggest_area = area
                    biggest_index = ind
                ind = ind + 1

        if len(detections) > 0:
            x, y, w, h = detections[biggest_index]
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 3)
            head_angle = remap(float(x + (float(w) / 2.0)), IN_MIN, IN_MAX, OUT_MIN, OUT_MAX)
            print('x: ' + str(x) + ', head: ' + str(head_angle))
        head_angle_ave = head_angle * head_angle_alpha + head_angle_ave * (1.0 - head_angle_alpha)
        kit.servo[0].angle = int(head_angle_ave)

        with output.condition:
            output.condition.notify_all()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')
        try:
            address = ('', 8000)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()
