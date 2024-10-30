# coding: utf-8
import Fabo_PCA9685
import time
import pkg_resources
import smbus
import cv2


# initialize the servo motor. 
BUSNUM=1
SERVO_HZ=50
INITIAL_VALUE=300
bus = smbus.SMBus(BUSNUM)
PCA9685 = Fabo_PCA9685.PCA9685(bus,INITIAL_VALUE)
PCA9685.set_hz(SERVO_HZ)
# this is the single channel of BUS0. 
channel=0

go = True

while go:
    for angle in range(150,300,10):
        PCA9685.set_channel_value(0,angle)
        PCA9685.set_channel_value(3,angle)
        value = PCA9685.get_channel_value(channel)
        print(value)
        time.sleep(0.1)


    for angle in range(300,150,-10):
        PCA9685.set_channel_value(0,angle)
        PCA9685.set_channel_value(3,angle)
        value = PCA9685.get_channel_value(channel)
        print(value)
        time.sleep(0.1)

    if cv2.waitKey(1) == ord('q'):
        go=False

