import cv2
import numpy as np
import time
import Fabo_PCA9685
import smbus
import RPi.GPIO as GPIO
import os
from collections import deque

# === BACK MOTOR ACTIVATION ===
os.system("sudo busybox devmem 0x6000d504 32 0x2")
os.system("sudo busybox devmem 0x700031fc 32 0x45")
os.system("sudo busybox devmem 0x70003248 32 0x46")
os.system("sudo busybox devmem 0x6000d100 32 0x00")

# === SERVO INITIALIZATION ===
BUSNUM = 1
SERVO_HZ = 50
INITIAL_VALUE = 300

bus = smbus.SMBus(BUSNUM)
PCA9685 = Fabo_PCA9685.PCA9685(bus, INITIAL_VALUE)
PCA9685.set_hz(SERVO_HZ)
SERVO_CHANNEL = 0

# Servo steering range
SERVO_MIN = 230
SERVO_MAX = 500

# === BACK MOTOR SETUP ===
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

my_pwm1 = GPIO.PWM(32, 100)  # 100 Hz
my_pwm2 = GPIO.PWM(33, 100)  # 100 Hz
INITIAL_DUTY_CYCLE = 50
my_pwm1.start(INITIAL_DUTY_CYCLE)
my_pwm2.start(INITIAL_DUTY_CYCLE)

# === CAMERA SETTINGS ===
dispW, dispH = 800, 600
flip = 0
camSet = (
    'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, '
    f'framerate=21/1 ! nvvidconv flip-method={flip} ! video/x-raw, '
    f'width={dispW}, height={dispH}, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
)
cam = cv2.VideoCapture(camSet)

# === PARAMETERS ===
KERNEL_SIZE = 11
CANNY_THRESHOLD_MIN = 10
CANNY_THRESHOLD_MAX = 30
BLUR_KERNEL_SIZE = 19

ROI_TOP = 70
ROI_BOTTOM = 90
ROI_LINE = ROI_TOP + (ROI_BOTTOM - ROI_TOP) // 2

LINE_NUMBER = 10
LINE_THICKNESS = 3

LINE_THRESHOLD = 150

ROLLING_BUFFER_SIZE = 3

# === ROLLING BUFFER ===
class RollingBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = deque(maxlen=size)
        self.sum = 0

    def add(self, value):
        if len(self.buffer) == self.size:
            self.sum -= self.buffer[0]
        self.buffer.append(value)
        self.sum += value

    def get_average(self):
        return int(self.sum / len(self.buffer)) if self.buffer else 0

rolling_buffer = RollingBuffer(ROLLING_BUFFER_SIZE)

# === MAIN LOOP ===
while True:
    ret, img = cam.read()
    if not ret:
        break

    _, _, r_channel = cv2.split(img)
    height, width = r_channel.shape

    # Define ROI
    roi = r_channel[ROI_TOP * height // 100 : ROI_BOTTOM * height // 100, :]

    # Apply Gaussian Blur
    blurred_roi = cv2.GaussianBlur(roi, (BLUR_KERNEL_SIZE, BLUR_KERNEL_SIZE), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred_roi, CANNY_THRESHOLD_MIN, CANNY_THRESHOLD_MAX)

    # Morphological closing
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (KERNEL_SIZE, KERNEL_SIZE * 2))
    closed_edges = cv2.dilate(edges, kernel, iterations=1)

    # Detect lines using Hough Transform
    lines = cv2.HoughLines(closed_edges, rho=1, theta=np.pi / 180 * 10, threshold=LINE_THRESHOLD)

    mask = np.zeros_like(r_channel, dtype=np.uint8)
    if lines is not None:
        sorted_lines = sorted(lines[:, 0], key=lambda x: abs(x[0]), reverse=True)
        for rho, theta in sorted_lines[:LINE_NUMBER]:
            a, b = np.cos(theta), np.sin(theta)
            x0, y0 = a * rho, b * rho
            x1, y1 = int(x0 + 1000 * -b), int(y0 + 1000 * a)
            x2, y2 = int(x0 - 1000 * -b), int(y0 - 1000 * a)
            cv2.line(mask, (x1, y1 + ROI_TOP * height // 100), (x2, y2 + ROI_TOP * height // 100), 255, LINE_THICKNESS)

    # Horizontal line for intersection
    horizontal_line = np.zeros_like(mask)
    cv2.line(horizontal_line, (0, ROI_LINE * height // 100), (width, ROI_LINE * height // 100), 255, LINE_THICKNESS)

    intersection = cv2.bitwise_and(mask, horizontal_line)

    # Find contours
    contours, _ = cv2.findContours(intersection, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x_coords = [int(cv2.moments(c)["m10"] / cv2.moments(c)["m00"]) for c in contours if cv2.moments(c)["m00"] != 0]

    if x_coords:
        avg_x = sum(x_coords) / len(x_coords)
        rolling_buffer.add(avg_x)
        servo_angle = int((avg_x / width) * (SERVO_MAX - SERVO_MIN) + SERVO_MIN)
        PCA9685.set_channel_value(SERVO_CHANNEL, servo_angle)
    else:
        print("No contours found.")

    # Visualization
    center = rolling_buffer.get_average()
    y_dot = ROI_LINE * height // 100
    output = cv2.cvtColor(r_channel, cv2.COLOR_GRAY2BGR)
    cv2.circle(output, (center, y_dot), 5, (255, 0, 0), -1)
    cv2.rectangle(output, (0, ROI_TOP * height // 100), (width, ROI_BOTTOM * height // 100), (0, 255, 0), 2)

    cv2.imshow("Processed", output)
    cv2.imshow("Edges", edges)

    if cv2.waitKey(1) == ord('q'):
        break

# === CLEANUP ===
cam.release()
cv2.destroyAllWindows()
my_pwm1.stop()
my_pwm2.stop()
GPIO.cleanup()
