import cv2
import numpy as np
import Jetson.GPIO as GPIO
import time

# here I will work on changing the color space and do some object tracking
# Image width and height
dispW = 800
dispH = 600
flip = 2


def nothing(x):
    pass

cv2.namedWindow('trackbars')
cv2.moveWindow('trackbars',int(dispW*1.2),0)
cv2.createTrackbar('hueLow','trackbars',0,179,nothing)
cv2.createTrackbar('hueHigh','trackbars',39,179,nothing)
cv2.createTrackbar('satLow','trackbars',63,255,nothing)
cv2.createTrackbar('satHigh','trackbars',225,255,nothing)
cv2.createTrackbar('valLow','trackbars',46,255,nothing)
cv2.createTrackbar('valHigh','trackbars',255,255,nothing)


cv2.namedWindow('converted')
cv2.moveWindow('converted',0,int(dispH))
cv2.namedWindow('cam')
cv2.moveWindow('cam', 0, 0)


# Uncomment These next Two Lines for Pi Camera
camSet = 'nvarguscamerasrc !  video/x-raw(memory:NVMM), \
        width=3264, height=2464, format=NV12, \
        framerate=21/1 ! nvvidconv flip-method=' + str(flip) + ' ! video/x-raw, \
        width=' + str(dispW) + ', height=' + str(dispH) + ', \
        format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'

cam = cv2.VideoCapture(camSet)



while True:
    # Grab image
    ret, img = cam.read()
    if not ret:
        break
    cv2.imshow('cam', img)
    
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    hueLow=cv2.getTrackbarPos('hueLow','trackbars')
    hueHigh=cv2.getTrackbarPos('hueHigh','trackbars')
    satLow=cv2.getTrackbarPos('satLow','trackbars')
    satHigh=cv2.getTrackbarPos('satHigh','trackbars')
    valLow=cv2.getTrackbarPos('valLow','trackbars')
    valHigh=cv2.getTrackbarPos('valHigh','trackbars')
    

    l_b=np.array([hueLow,satLow,valLow])
    h_b=np.array([hueHigh,satHigh,valHigh])

    mask=cv2.inRange(hsv,l_b,h_b)
    kernel=np.ones((5,5),np.uint8)
    mask=cv2.erode(mask,kernel)
    mask=cv2.dilate(mask,kernel)
    

    FG=cv2.bitwise_and(img,img,mask=mask)


    cv2.imshow('converted', FG)

    

    if cv2.waitKey(1) == ord('q'):
        break

# Cleanupq
cam.release()
GPIO.cleanup()  # Reset GPIO settings
cv2.destroyAllWindows()
