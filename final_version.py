import RPi.GPIO as GPIO
import time
import os
import pygame
import Fabo_PCA9685
import pkg_resources
import smbus
import cv2
from collections import deque

def rolling_buffer(buffer, value, size):
    if len(buffer) == size:
        buffer.popleft()
    buffer.append(value)
    return sum(buffer) / len(buffer)


# set up the camera
width=1100
height=800
flip=0
camSet = (
    'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, '
    f'framerate=21/1 ! nvvidconv flip-method={flip} ! video/x-raw, '
    f'width={width}, height={height}, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
)
cam= cv2.VideoCapture(camSet)


# PWM setup
os.system("sudo busybox devmem 0x6000d504 32 0x2")
os.system("sudo busybox devmem 0x700031fc 32 0x45")
os.system("sudo busybox devmem 0x70003248 32 0x46")
os.system("sudo busybox devmem 0x6000d100 32 0x00")
os.system("export DBUS_FATAL_WARNINGS=0")


# initialize servo steering motor
BUSNUM=1
SERVO_HZ=50
INITIAL_VALUE=300
bus = smbus.SMBus(BUSNUM)
PCA9685 = Fabo_PCA9685.PCA9685(bus,INITIAL_VALUE)
PCA9685.set_hz(SERVO_HZ)
channel=0
go = True

# steering edges and middle
# middle=365, deviation=135
start=230
stop=500


# Activate back motors
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

# Start PWM
my_pwm1 = GPIO.PWM(32, 100)  # 100 Hz
my_pwm2 = GPIO.PWM(33, 100)  # 100 Hz

# Start the motor with an initial duty cycle
duty_cycle = 50
my_pwm1.start(duty_cycle)

# Servo steering range
SERVO_MIN = 230
SERVO_MAX = 500

# rolling buffer definition:
ROLLING_BUFFER_SIZE = 3
buffer = deque(maxlen=ROLLING_BUFFER_SIZE)



def calculate_centroid(contours):
    centroids = []
    for cnt in contours:
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            centroids.append((cx, cy))
        else:
            # If the area (m00) is zero, the centroid is undefined; skip or handle as needed
            print("Contour with zero area, centroid undefined.")
    return centroids


def calculate_average_x(centroids):
    if len(centroids) == 0:
        print("No centroids to calculate the average.")
        return None
    total_x = sum(cx for cx, cy in centroids)
    average_x = total_x / len(centroids)
    return int(average_x)




def plot_two2(imgG, imgB, roi_start, roi_height, contoursG, contoursB, centerB, centerG, scalemain):
    if imgG is None or imgB is None:
        print("Error: One or both images are invalid.")
        return

    x_dim, y_dim = imgG.shape
    scale = 2.5
    x_dim_plot = int(x_dim / scale)
    y_dim_plot = int(y_dim / scale)
    # print("x_dim_plot:", x_dim_plot, "y_dim_plot:", y_dim_plot)

    # Convert grayscale images to BGR for visualization
    imgG = cv2.cvtColor(imgG, cv2.COLOR_GRAY2BGR)
    imgB = cv2.cvtColor(imgB, cv2.COLOR_GRAY2BGR)

    # Translate contours by applying an offset to the y-coordinate
    translated_contoursB = [contour + [0, roi_start] for contour in contoursB]
    translated_contoursG = [contour + [0, roi_start] for contour in contoursG]

    # Draw translated contours on the images
    cv2.drawContours(imgB, translated_contoursB, -1, (255, 0, 0), 2)
    cv2.drawContours(imgG, translated_contoursG, -1, (0, 255, 0), 2)

    # circle 
    radius=3
    if centerB:
        cv2.circle(imgB, (centerB, int(roi_start+roi_height/2)), radius, (255, 0, 0), 10)
    
    if centerG:
        cv2.circle(imgG, (centerG, int(roi_start+roi_height/2)), radius, (0, 255, 0), 10)

    # Create named windows for resizing
    cv2.namedWindow("imgB", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("imgB", y_dim_plot, x_dim_plot)
    cv2.moveWindow("imgB",0,0)
    cv2.imshow("imgB", imgB)

    cv2.namedWindow("imgG", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("imgG", y_dim_plot, x_dim_plot)
    cv2.moveWindow("imgG",int(y_dim_plot*1.2),0)
    cv2.imshow("imgG", imgG)



weigthed_center=0
try:
    while True:
        
        ret, img = cam.read()
        cv2.imshow('nanoCam',img)
        cv2.moveWindow("nanoCam", 0, 0)

        # calculate roi
        roi_width =  int(width*1.0)
        roi_height = int(height*0.15)
        roi_start=int(height/100*65)

        # Calculate top-left and bottom-right corners of the rectangle
        #  and draw the rectangle
        top_left = (int((width - roi_width) // 2), roi_start)
        bottom_right = (top_left[0] + roi_width, top_left[1] + roi_height)
        cv2.rectangle(img, top_left, bottom_right, (0, 0, 0), 1)

        imgB,imgG,imgR = cv2.split(img)
    
        # cv2.imshow("imgB",imgB) 
        # cv2.imshow("imgG",imgG)
        # cv2.imshow("imgR",imgR)
        

        # define the roi in blue and green channels. 
        roiB = imgB[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        roiG = imgG[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

        # blur the 2 roi
        filter_size=25
        roiB = cv2.GaussianBlur(roiB,(filter_size,filter_size),0)
        roiG = cv2.GaussianBlur(roiG,(filter_size,filter_size),0)

        # calcualte the avg color in each channel
        avgB = cv2.mean(roiB)[0]
        avgG = cv2.mean(roiG)[0]

        # find also the min and max in the roi
        (minValB, maxValB, _, _) = cv2.minMaxLoc(roiB)
        (minValG, maxValG, _, _) = cv2.minMaxLoc(roiG)


        # threshold. define the thresholds considering the min max and avg. 
        Blue_thresh  = max (100,int(avgB*1.25))
        Green_thresh = max(20,int(avgG*1.3))

        # probably there is no line in the image. do not detect a line
        if((maxValB-minValB)<50):
            Blue_thresh=255
        
        # if((maxValG-minValG)<20):
        #     Green_thresh=255


        # apply the threshold in each channel
        _, Bt = cv2.threshold(roiB, Blue_thresh, 255, cv2.THRESH_BINARY )
        _, Gt = cv2.threshold(roiG, Green_thresh, 255, cv2.THRESH_BINARY )

        cv2.imshow("green thresh out",Gt)
        

        # detect the countours
        contoursB, _ = cv2.findContours(Bt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contoursG, _ = cv2.findContours(Gt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        # Define a minimum and maximum area threshold
        min_area = 200  # Adjust as needed
        max_area = 30000  # Adjust as needed

        # Filter contours by area for blue threshold with area printing
        filtered_contoursB = []
        for cnt in contoursB:
            area = cv2.contourArea(cnt)
            if min_area <= area <= max_area:
                filtered_contoursB.append(cnt)

        # Filter contours by area for green threshold with area printing
        filtered_contoursG = []
        for cnt in contoursG:
            area = cv2.contourArea(cnt)
            if min_area <= area <= max_area:
                filtered_contoursG.append(cnt)


        # trova i centroidi 
        centroidsB = calculate_centroid(filtered_contoursB)
        centroidsG = calculate_centroid(filtered_contoursG)

        # average position of the centroids that I find. 
        avgB_c=calculate_average_x(centroidsB)
        avgG_c=calculate_average_x(centroidsG)

        print("centroidsB: ",centroidsB," avg: ",avgB_c)
        print("centroidsG: ",centroidsG," avg: ",avgG_c)

        # modify the global centro variables if something has been detected
        if avgB_c:
            centroB = avgB_c
        else:
            centroB = None
        
        if avgG_c:
            centroG = avgG_c
        else:
            centroG = None

        if centroB and centroG:
            weigthed_center = int( (centroG * 0.8 + centroB * 0.2)  )
        elif centroB:
            weigthed_center = centroB
        elif centroG:
            weigthed_center = centroG
        

        cv2.circle(img, (weigthed_center, int(roi_start+roi_height/2)), 3, (0, 0, 255), 10)


        if weigthed_center:
            angle_avg=rolling_buffer(buffer, weigthed_center, ROLLING_BUFFER_SIZE)
            # rb.add(weigthed_center)
            # avg_angle=rb.get_average()
            servo_angle = int((angle_avg / width) * (SERVO_MAX - SERVO_MIN) + SERVO_MIN)
            PCA9685.set_channel_value(channel, servo_angle)

        scale_img=1
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("img", int(width/scale_img), int(height/scale_img))
        cv2.moveWindow("img",0,0)
        cv2.imshow("img",img)


        # plot the 2 images together. 
        plot_two2(imgG,imgB,roi_start,roi_height,filtered_contoursG,filtered_contoursB,centroB,centroG,scale_img)

        

        if cv2.waitKey(1) == ord('q'):
            break



# closing up everything
finally:
    print("Cleaning up resources...")
    my_pwm1.stop()
    my_pwm2.stop()
    GPIO.cleanup()
    cam.release()
    cv2.destroyAllWindows()
    pygame.quit()