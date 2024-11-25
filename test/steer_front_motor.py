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

# middle=365, deviation=135
start=230
stop=500



delay=0.05
# PCA9685.set_channel_value(3,(stop-start)/2)

while go:
    for angle in range(start,stop,10):
        PCA9685.set_channel_value(0,angle)
        PCA9685.set_channel_value(3,angle)
        value = PCA9685.get_channel_value(channel)
        print(value)
        time.sleep(delay)


    for angle in range(stop,start,-10):
        PCA9685.set_channel_value(0,angle)
        PCA9685.set_channel_value(3,angle)
        value = PCA9685.get_channel_value(channel)
        print(value)
        time.sleep(delay)

    if cv2.waitKey(1) == ord('q'):
        go=False

