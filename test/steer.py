# script.py
import sys
from adafruit_servokit import ServoKit
import board
import busio

kit = ServoKit(channels=16,address=0x40)

def my_function(arg):
    print("Angle received: ",arg)
    kit.servo[0].angle=int(arg)

if __name__ == "__main__":
    my_function(sys.argv[1])

