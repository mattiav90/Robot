import RPi.GPIO as GPIO
import time
import os
import pygame
import Fabo_PCA9685
import pkg_resources
import smbus
import cv2

# -------------------------------------------
# run this int the shell
# export DBUS_FATAL_WARNINGS=0
# -------------------------------------------


print(cv2.__version__)
dispW=1100
dispH=800
flip=0
#Uncomment These next Two Line for Pi Camera
shutter_speed = 100000000  # Set desired shutter speed in microseconds (e.g., 1/30 sec)

# Construct GStreamer command
camSet = f"nvarguscamerasrc exposuretimerange={shutter_speed},{shutter_speed} ! " \
         f"video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! " \
         f"nvvidconv flip-method={flip} ! video/x-raw, width={dispW}, height={dispH}, format=BGRx ! " \
         f"videoconvert ! video/x-raw, format=BGR ! appsink"
cam= cv2.VideoCapture(camSet)




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
os.system("export DBUS_FATAL_WARNINGS=0")

# Set this for the joystick
os.environ['DBUS_FATAL_WARNINGS'] = '0'

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
duty_cycle = 0
my_pwm1.start(duty_cycle)
my_pwm2.start(duty_cycle)

# Main loop
try:
    while True:
        pygame.event.pump()  # Process events

        # accelerate
        axis_value = joystick.get_axis(3)  # Assuming axis 0 is the relevant axis
        duty_cycle = (-1*axis_value * 100)   # Scale -1 to 1 -> 0 to 100

        if duty_cycle>=0:
            my_pwm1.ChangeDutyCycle(duty_cycle)
            my_pwm2.ChangeDutyCycle(0)
        else:
            duty_cycle=-1*duty_cycle
            my_pwm1.ChangeDutyCycle(0)
            my_pwm2.ChangeDutyCycle(duty_cycle)

        # steer looking a axis 0. 365
        steer=joystick.get_axis(0)*135+360
        steer=max(135, min(500, steer))
        PCA9685.set_channel_value(0,steer)

        ret, frame = cam.read()
        cv2.imshow('nanoCam',frame)
        cv2.moveWindow("nanoCam", 0, 0)

        # Print axis values
        for i in range(joystick.get_numaxes()):
            print(f"Axis {i}: {joystick.get_axis(i):.3f}.", end="  ")

        print("\r", end="")  # Stay on the same line

        # Break the loop on 'q' key press
        if cv2.waitKey(1) == ord('q'):
            break

except KeyboardInterrupt:
    print("\nKeyboardInterrupt detected. Exiting gracefully...")

finally:
    # Cleanup
    print("Cleaning up resources...")
    my_pwm1.stop()
    my_pwm2.stop()
    GPIO.cleanup()
    cam.release()
    cv2.destroyAllWindows()
    pygame.quit()