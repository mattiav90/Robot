import cv2
import numpy as np
import Jetson.GPIO as GPIO
import time

# Image width and height
dispW = 800
dispH = 600
flip = 0

# Uncomment These next Two Lines for Pi Camera
camSet = 'nvarguscamerasrc !  video/x-raw(memory:NVMM), \
        width=3264, height=2464, format=NV12, \
        framerate=21/1 ! nvvidconv flip-method=' + str(flip) + ' ! video/x-raw, \
        width=' + str(dispW) + ', height=' + str(dispH) + ', \
        format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'

cam = cv2.VideoCapture(camSet)

def nothing(x):
    pass

cv2.namedWindow('cam')
cv2.namedWindow('cam1')
cv2.createTrackbar('x1', 'cam', 230, 500, nothing)
cv2.createTrackbar('x2', 'cam', 320, 500, nothing)
cv2.createTrackbar('x3', 'cam', 0, 500, nothing)
cv2.createTrackbar('x4', 'cam', 10, 500, nothing)
cv2.moveWindow('cam', 0, 0)

# Set a minimum area for contours to be considered "big"
min_area = 70  # You can adjust this value as needed

while True:
    # Grab image
    ret, img = cam.read()
    if not ret:
        break

    x1 = cv2.getTrackbarPos('x1', 'cam')
    x2 = cv2.getTrackbarPos('x2', 'cam')
    x3 = cv2.getTrackbarPos('x3', 'cam')
    x4 = cv2.getTrackbarPos('x4', 'cam')
    x5 = cv2.getTrackbarPos('x5', 'cam')
    print(x1)
    print(x2)
    print(x3)
    print(x4)

    # Get dimensions
    height, width, _ = img.shape
    
    # Define the ROI (bottom half)
    roi_start_y = height // 2
    roi_end_y = height
    img = img[roi_start_y:roi_end_y, 0:width]  # Slicing to get the bottom half
    # re set based on the new shape
    height, width, _ = img.shape

    # blur a littlebit the image
    kernel=np.ones((5,5),np.float32)/25
    dst=cv2.filter2D(img,-1,kernel)

    # convert in grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(gray, x1, x2)

    # dilate a little bit the found edges
    kernel=np.ones((5,5),np.float32)/50
    edges = cv2.dilate(edges,kernel,iterations=1)

    # draw a line at the bottom of the image
    cv2.line(edges, (0, height - 1), (width - 1, height - 1), (255), thickness=3)  # Draws a white line
    cv2.line(edges, (0, 1), (width - 1, 1), (255), thickness=3)  # Draws a white line

    # open
    # edges =  cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)



    # Step 3: Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # create a mask
    mask=np.zeros(img.shape,np.uint8)
    # fill the poligons that are found in contours
    cv2.fillPoly(mask,contours,255)

    # open
    kernel=np.ones((20,20),np.float32)/50
    # mask =  cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


    # erode
    mask= cv2.erode(mask,kernel,iterations = 1)



    # Display the original image with the edge-detected ROI
    cv2.imshow('cam', img)
    cv2.imshow('cam1', mask)
    

    if cv2.waitKey(1) == ord('q'):
        break

# Cleanupq
cam.release()
# GPIO.cleanup()  # Reset GPIO settings
cv2.destroyAllWindows()
