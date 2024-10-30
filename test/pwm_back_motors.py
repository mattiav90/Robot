import RPi.GPIO as GPIO
import time
import os
# import keyboard  # Import the keyboard library

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

os.system("sudo busybox devmem 0x6000d504 32 0x2")
os.system("sudo busybox devmem 0x700031fc 32 0x45")
os.system("sudo busybox devmem 0x70003248 32 0x46")
os.system("sudo busybox devmem 0x6000d100 32 0x00")


#activate back motors

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)

# Start PWM
my_pwm1 = GPIO.PWM(32, 100)  # 100 Hz
my_pwm2 = GPIO.PWM(33, 100)  # 100 Hz
duty_cycle = 90  # Initial duty cycle (10%)
my_pwm1.start(duty_cycle)
# my_pwm2.start(duty_cycle)


time.sleep(10)


# Cleanup
my_pwm1.stop()
my_pwm2.stop()
GPIO.cleanup()
