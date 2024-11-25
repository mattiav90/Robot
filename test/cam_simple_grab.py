import cv2
import os

print(cv2.__version__)
dispW=900
dispH=700
flip=0
#Uncomment These next Two Line for Pi Camera
shutter_speed = 100000000  # Set desired shutter speed in microseconds (e.g., 1/30 sec)

# Construct GStreamer command
camSet = f"nvarguscamerasrc exposuretimerange={shutter_speed},{shutter_speed} ! " \
         f"video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! " \
         f"nvvidconv flip-method={flip} ! video/x-raw, width={dispW}, height={dispH}, format=BGRx ! " \
         f"videoconvert ! video/x-raw, format=BGR ! appsink"


# gst-launch-1.0 nvarguscamerasrc exposuretimerange="13000 13000"    .... .. .
cam= cv2.VideoCapture(camSet)


 
#Or, if you have a WEB cam, uncomment the next line
#(If it does not work, try setting to '1' instead of '0')
#cam=cv2.VideoCapture(0)
while True:
    ret, frame = cam.read()
    cv2.imshow('nanoCam',frame)
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
