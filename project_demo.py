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

def nothing():
    pass

cv2.namedWindow('cam')
cv2.namedWindow('cam1')
cv2.createTrackbar('x1', 'cam', 1, 10, nothing)
cv2.createTrackbar('x2', 'cam', 1, 10, nothing)
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
    # roi_start_y = height // 2
    # roi_end_y = height
    # roi = img[roi_start_y:roi_end_y, 0:width]  # Slicing to get the bottom half

    # Convert ROI to grayscale for edge detection
    # roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(gray, 100, 250)

    # kernel=np.ones((2,2),np.uint8)
    # opened=cv2.morphologyEx(edges,cv2.MORPH_OPEN,kernel)

    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
    dilated=cv2.dilate(edges,kernel,iterations=1)
    
    kernel_erode=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(20,20))
    eroded=cv2.erode(dilated,kernel_erode,iterations=1)
    dilated2=cv2.dilate(eroded,kernel,iterations=1)


    # Apply a binary threshold to the edges
    _, thresholded_edges = cv2.threshold(dilated2, 100, 250, cv2.THRESH_BINARY)

    # Find contours
    contours, hierarchy = cv2.findContours(thresholded_edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    for c in contours:
        if cv2.contourArea(c)>1000:
            # print("area: ",cv2.contourArea(c))
            cv2.drawContours(img,c,-1,(0,0,255),2)
    


    # Draw a rectangle around the ROI on the original image
    # cv2.rectangle(img, (0, roi_start_y), (width, roi_end_y), (0, 255, 0), 2)

    # Display the original image with the edge-detected ROI
    cv2.imshow('cam', img)
    cv2.imshow('cam1', edges)
    

    if cv2.waitKey(1) == ord('q'):
        break

# Cleanupq
cam.release()
GPIO.cleanup()  # Reset GPIO settings
cv2.destroyAllWindows()
