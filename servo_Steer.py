from adafruit_servokit import ServoKit
import board
import busio
import time


# to detect the connected i2c devices use:
# sudo i2cdetect -y -r 1
# sudo i2cdetect -y -r 0


kit = ServoKit(channels=16,address=0x40)


# sweep from 10 to 170. the center is circa 75. 
# 6V alimentation is sufficient

kit.servo[0].angle=10
time.sleep(1)

sweep = range(10,170,5)
for i in sweep:
    kit.servo[0].angle=i
    print("angle: ",i)
    time.sleep(0.2)


kit.servo[0].angle=75

