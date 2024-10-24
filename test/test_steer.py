# coding: utf-8
import Fabo_PCA9685
import time
import pkg_resources
import smbus



# initialize the servo motor. 
BUSNUM=1
SERVO_HZ=50
INITIAL_VALUE=300
bus = smbus.SMBus(BUSNUM)
PCA9685 = Fabo_PCA9685.PCA9685(bus,INITIAL_VALUE)
PCA9685.set_hz(SERVO_HZ)
# this is the single channel of BUS0. 
channel=0


for angle in range(110,480,10):
    PCA9685.set_channel_value(channel,angle)
    value = PCA9685.get_channel_value(channel)
    print(value)
    time.sleep(0.05)


for angle in range(480,110,-10):
    PCA9685.set_channel_value(channel,angle)
    value = PCA9685.get_channel_value(channel)
    print(value)
    time.sleep(0.05)

