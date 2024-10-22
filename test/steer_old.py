from adafruit_servokit import ServoKit
import time

# Initialize the ServoKit
kit = ServoKit(channels=16, address=0x40)

def set_steering_position(x, img_width):
   
    angle= (x/img_width)*180

    if angle < 0 or angle > 180:
        raise ValueError("Angle must be between 0 and 180 degrees.")
    
    if angle<10:
        angle=10
    
    if angle>170:
        angle=170


    kit.servo[0].angle = angle
    print(f"Steering angle set to: {angle} degrees")
    # time.sleep(0.2)  # Optional delay for smoother operation
