import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(33, GPIO.OUT)

# Start PWM
my_pwm = GPIO.PWM(33, 100)  # 100 Hz
my_pwm.start(50)  # 50% duty cycle

try:
    while True:
        time.sleep(1)  # Keep the program running
except KeyboardInterrupt:
    pass  # Exit on Ctrl+C

# Cleanup
my_pwm.stop()
GPIO.cleanup()
