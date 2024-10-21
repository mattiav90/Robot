import cv2
import numpy as np
import Jetson.GPIO as GPIO
import time
# import matplotlib.pyplot as plt


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

# windows for images
cv2.namedWindow('cam')
cv2.namedWindow('cam1')
cv2.namedWindow('cam2')
# positions of windows
cv2.moveWindow('cam', 0, 0)
cv2.moveWindow('cam1', 500, 0)
cv2.moveWindow('cam2', 500, 500)


cv2.createTrackbar('x1', 'cam', 110, 500, nothing)
cv2.createTrackbar('x2', 'cam', 250, 500, nothing)
cv2.createTrackbar('x3', 'cam', 100, 500, nothing)
cv2.createTrackbar('x4', 'cam', 255, 500, nothing)

# Set a minimum area for contours to be considered "big"
min_area = 70  # You can adjust this value as needed


# def plot_histogram(image):
#     """Plot the histogram of an image."""
#     plt.clf()  # Clear the previous histogram
#     color = ('b', 'g', 'r')
#     for i, col in enumerate(color):
#         histr = cv2.calcHist([image], [i], None, [256], [0, 256])
#         plt.plot(histr, color=col)
#         plt.xlim([0, 256])
#     plt.draw()  # Update the plot
#     plt.pause(1)  # Pause to allow the plot to update

kernel_soft=np.ones((5,5),np.float32)/20
kernel_hard=np.ones((7,7),np.float32)/3


while True:
    # Grab image
    ret, img = cam.read()
    if not ret:
        break

    # plot the histogram 
    # plot_histogram(img)
    
    
    x1 = cv2.getTrackbarPos('x1', 'cam')
    x2 = cv2.getTrackbarPos('x2', 'cam')
    x3 = cv2.getTrackbarPos('x3', 'cam')
    x4 = cv2.getTrackbarPos('x4', 'cam')
    

    # Get dimensions
    height, width, _ = img.shape
    
    # Define the ROI (bottom half)
    roi_start_y = height // 2
    roi_end_y = height
    img = img[roi_start_y:roi_end_y, 0:width]  # Slicing to get the bottom half
    # re set based on the new shape
    height, width, _ = img.shape

    grey= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # blur a littlebit the image
    dst=cv2.filter2D(grey,-1,kernel_soft)

    # Step 1: Threshold the image
    _, thresh1 = cv2.threshold(dst, x3, x4, cv2.THRESH_BINARY)

    # erode
    thresh1= cv2.erode(thresh1,kernel_hard,iterations = 1)
    # Step 3: Find contours
    contours, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Step 4: Approximate the contours
    approx_contours = [cv2.approxPolyDP(c, 0.001 * cv2.arcLength(c, True), True) for c in contours]

    x=0
    # Optionally, draw the approximated contours on the original image
    for c in approx_contours:

        x,y,w,h = cv2.boundingRect(c)
        aspect_ratio = float(w)/h
        area=cv2.contourArea(c)
        if (aspect_ratio<0.5) and area>10000:
            (x,y),(MA,ma),angle = cv2.fitEllipse(c)
            ratio=ma/MA
            # print("MA: ",MA," ma: ",ma," ratio: ",ratio)

            if ratio>10:
                cv2.drawContours(img, [c], -1, (0, 0, 255), 2) 
                M = cv2.moments(c)

                # Calculate the centroid coordinates
                x = int(M['m10'] / M['m00'])
                y = int(M['m01'] / M['m00'])
                print("x: ",x)

                



              









    # Display the original image with the edge-detected ROI
    cv2.imshow('cam', img)
    # cv2.imshow('cam1', contours)
    cv2.imshow('cam2', thresh1)
    
    

    if cv2.waitKey(1) == ord('q'):
        break

# Cleanupq
cam.release()
# GPIO.cleanup()  # Reset GPIO settings
cv2.destroyAllWindows()
# cam.release()
# plt.ioff()  # Disable interactive mode
# plt.show()  # Show the final plot (optional)