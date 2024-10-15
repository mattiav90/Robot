import RPi.GPIO as GPIO
import time
import keyboard  # Import the keyboard library

# might be helpful
# https://forums.developer.nvidia.com/t/nano-pwm0-cant-work/157462/11
# https://forums.developer.nvidia.com/t/jetson-nano-pwm-not-working/154939/17

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)

# Start PWM
my_pwm = GPIO.PWM(32, 100)  # 100 Hz
duty_cycle = 10  # Initial duty cycle (10%)
my_pwm.start(duty_cycle)

try:
    while True:
        # Check for key presses
        if keyboard.is_pressed('up'):  # If the up arrow is pressed
            duty_cycle = min(duty_cycle + 10, 100)  # Increase duty cycle, max 100%
            my_pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)  # Delay to prevent rapid increase

        elif keyboard.is_pressed('down'):  # If the down arrow is pressed
            duty_cycle = max(duty_cycle - 10, 0)  # Decrease duty cycle, min 0%
            my_pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)  # Delay to prevent rapid decrease

        time.sleep(0.1)  # Small delay to prevent CPU overload

except KeyboardInterrupt:
    pass  # Exit on Ctrl+C

# Cleanup
my_pwm.stop()
GPIO.cleanup()
