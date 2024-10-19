import RPi.GPIO as GPIO
import time
import keyboard  # Import the keyboard library

# might be helpful
# https://forums.developer.nvidia.com/t/nano-pwm0-cant-work/157462/11
# https://forums.developer.nvidia.com/t/jetson-nano-pwm-not-working/154939/17


# pin 33
# sudo busybox devmem 0x70003248 32 0x46
# sudo busybox devmem 0x6000d100 32 0x00
# 
# pin 32
# sudo busybox devmem 0x700031fc 32 0x45
# sudo busybox devmem 0x6000d504 32 0x2


# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)

# Start PWM
my_pwm1 = GPIO.PWM(32, 100)  # 100 Hz
my_pwm2 = GPIO.PWM(33, 100)  # 100 Hz
duty_cycle = 50  # Initial duty cycle (10%)
my_pwm1.start(duty_cycle)
my_pwm2.start(duty_cycle)

try:
    while True:
        # Check for key presses
        if keyboard.is_pressed('up'):  # If the up arrow is pressed
            duty_cycle = min(duty_cycle + 10, 100)  # Increase duty cycle, max 100%
            my_pwm1.ChangeDutyCycle(duty_cycle)
            my_pwm2.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)  # Delay to prevent rapid increase

        elif keyboard.is_pressed('down'):  # If the down arrow is pressed
            duty_cycle = max(duty_cycle - 10, 0)  # Decrease duty cycle, min 0%
            my_pwm1.ChangeDutyCycle(duty_cycle)
            my_pwm2.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)  # Delay to prevent rapid decrease

        time.sleep(0.1)  # Small delay to prevent CPU overload

except KeyboardInterrupt:
    pass  # Exit on Ctrl+C

# Cleanup
my_pwm1.stop()
my_pwm2.stop()
GPIO.cleanup()
