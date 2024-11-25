import RPi.GPIO as GPIO
import os
import pygame
import Fabo_PCA9685
import smbus

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
os.environ['DBUS_FATAL_WARNINGS'] = '0'

# Initialize servo motor for steering
BUSNUM = 1
SERVO_HZ = 50
INITIAL_VALUE = 300
bus = smbus.SMBus(BUSNUM)
PCA9685 = Fabo_PCA9685.PCA9685(bus, INITIAL_VALUE)
PCA9685.set_hz(SERVO_HZ)

# Servo control range
STEERING_MIN = 230
STEERING_MAX = 500
STEERING_MID = 365
STEERING_DEVIATION = 135

# Activate back motors
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

# Start PWM for back motors
motor_pwm1 = GPIO.PWM(32, 100)  # 100 Hz
motor_pwm2 = GPIO.PWM(33, 100)  # 100 Hz
motor_pwm1.start(0)
motor_pwm2.start(0)

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

        # Steer
        steer = joystick.get_axis(0) * STEERING_DEVIATION + STEERING_MID
        steer = max(STEERING_MIN, min(STEERING_MAX, steer))  # Clamp steering range
        PCA9685.set_channel_value(0, steer)

        # Print joystick axis values
        for i in range(joystick.get_numaxes()):
            print(f"Axis {i}: {joystick.get_axis(i):.3f}", end="  ")
        print("\r", end="")  # Stay on the same line

        # Break the loop on 'q' key press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            print("Exiting loop on 'q' key press.")
            break

except KeyboardInterrupt:
    print("\nKeyboardInterrupt detected. Exiting gracefully...")

finally:
    # Cleanup
    print("Cleaning up resources...")
    motor_pwm1.stop()
    motor_pwm2.stop()
    GPIO.cleanup()
    pygame.quit()
