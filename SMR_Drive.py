import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import pyrebase

# Initialize Firebase configuration - Replace with your Firebase project credentials
firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_AUTH_DOMAIN",
    "databaseURL": "YOUR_DATABASE_URL",
    "storageBucket": "YOUR_STORAGE_BUCKET"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
storage = firebase.storage()
db = firebase.database()

# Define GPIO pins for motor control
left_motor_forward = 17
left_motor_backward = 18
right_motor_forward = 22
right_motor_backward = 23

# Set up GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(left_motor_forward, GPIO.OUT)
GPIO.setup(left_motor_backward, GPIO.OUT)
GPIO.setup(right_motor_forward, GPIO.OUT)
GPIO.setup(right_motor_backward, GPIO.OUT)

# Define GPIO pins for Ultrasonic sensor
ultrasonic_trigger = 24
ultrasonic_echo = 25

# Set up Ultrasonic sensor GPIO pins
GPIO.setup(ultrasonic_trigger, GPIO.OUT)
GPIO.setup(ultrasonic_echo, GPIO.IN)

# Initialize the camera
camera = cv2.VideoCapture(0)  # Use 0 for the default camera (you may need to change this)

# Function to move the robot forward
def move_forward():
    GPIO.output(left_motor_forward, GPIO.HIGH)
    GPIO.output(left_motor_backward, GPIO.LOW)
    GPIO.output(right_motor_forward, GPIO.HIGH)
    GPIO.output(right_motor_backward, GPIO.LOW)

# Function to turn the robot right
def turn_right():
    GPIO.output(left_motor_forward, GPIO.HIGH)
    GPIO.output(left_motor_backward, GPIO.LOW)
    GPIO.output(right_motor_forward, GPIO.LOW)
    GPIO.output(right_motor_backward, GPIO.HIGH)

# Function to stop the robot
def stop():
    GPIO.output(left_motor_forward, GPIO.LOW)
    GPIO.output(left_motor_backward, GPIO.LOW)
    GPIO.output(right_motor_forward, GPIO.LOW)
    GPIO.output(right_motor_backward, GPIO.LOW)

# Function to measure distance using Ultrasonic sensor
def measure_distance():
    GPIO.output(ultrasonic_trigger, True)
    time.sleep(0.00001)
    GPIO.output(ultrasonic_trigger, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ultrasonic_echo) == 0:
        start_time = time.time()

    while GPIO.input(ultrasonic_echo) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # Speed of sound is 343 m/s

    return distance

try:
    while True:
        # Measure distance using Ultrasonic sensor
        distance = measure_distance()

        # Adjust this threshold based on your robot's physical characteristics
        obstacle_threshold = 30  # In centimeters

        if distance <= obstacle_threshold:
            # Obstacle detected, stop and turn right (adjust as needed)
            stop()
            time.sleep(1)  # Pause for a moment
            turn_right()
            time.sleep(1)  # Adjust turn duration as needed
        else:
            # No obstacle, move forward
            move_forward()

        # Capture a frame from the camera
        ret, frame = camera.read()
        
        if not ret:
            break

        # Encode the frame as JPEG
        _, encoded_frame = cv2.imencode('.jpg', frame)
        
        # Convert the encoded frame to bytes
        frame_bytes = encoded_frame.tobytes()

        # Upload the frame to Firebase Cloud Storage
        storage.child("video_frames/frame.jpg").put(frame_bytes)

        # Update Firebase Realtime Database with sensor data
        db.child("sensor_data").set({"distance": distance})

except KeyboardInterrupt:
    # Clean up GPIO and release the camera on program exit
    GPIO.cleanup()
    camera.release()
    cv2.destroyAllWindows()
