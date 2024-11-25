import RPi.GPIO as GPIO
import time
import os
import pygame
import Fabo_PCA9685
import pkg_resources
import smbus
import cv2

# Initialize Pygame and the joystick
pygame.init()
pygame.joystick.init()

# Check for joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected!")
    pygame.quit()
    exit()

# Use the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick connected: {joystick.get_name()}")

# Set this for the PWM
os.system("sudo busybox devmem 0x6000d504 32 0x2")
os.system("sudo busybox devmem 0x700031fc 32 0x45")
os.system("sudo busybox devmem 0x70003248 32 0x46")
os.system("sudo busybox devmem 0x6000d100 32 0x00")

# Set this for the joystick
os.environ["DBUS_FATAL_WARNINGS"] = "0"

# initialize servo motor for steering 
BUSNUM=1
SERVO_HZ=50
INITIAL_VALUE=300
bus = smbus.SMBus(BUSNUM)
PCA9685 = Fabo_PCA9685.PCA9685(bus,INITIAL_VALUE)
PCA9685.set_hz(SERVO_HZ)
# this is the single channel of BUS0. 
channel=0
go = True

# middle=365, deviation=135
start=230
stop=500



# Activate back motors
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

# Start PWM
my_pwm1 = GPIO.PWM(32, 100)  # 100 Hz
my_pwm2 = GPIO.PWM(33, 100)  # 100 Hz

# Start the motor with an initial duty cycle
duty_cycle = 10
my_pwm1.start(duty_cycle)
my_pwm2.start(duty_cycle)

# Main loop
try:
    while True:
        pygame.event.pump()  # Process events

        # Scale joystick axis to duty cycle range (0-100)
        axis_value = joystick.get_axis(1)  # Assuming axis 0 is the relevant axis
        duty_cycle = (-1*axis_value * 100)   # Scale -1 to 1 -> 0 to 100

        # Update PWM
        duty_cycle = max(0, min(100, duty_cycle))  # Ensure within valid range
        my_pwm1.ChangeDutyCycle(duty_cycle)
        my_pwm2.ChangeDutyCycle(duty_cycle)

        # steer looking a axis 0. 
        steer=joystick.get_axis(0)*135+365
        PCA9685.set_channel_value(0,steer)

        # Print axis values
        for i in range(joystick.get_numaxes()):
            print(f"Axis {i}: {joystick.get_axis(i):.3f}", end="  ")

        print("\r", end="")  # Stay on the same line

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    # Cleanup
    my_pwm1.stop()
    my_pwm2.stop()
    GPIO.cleanup()
    pygame.quit()
