import RPi.GPIO as GPIO
import time
import os
import pygame
import Fabo_PCA9685
import pkg_resources
import smbus
import cv2
from collections import deque
from builtins import open



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
# this sets the speed of the motor.
duty_cycle = 0
my_pwm1.start(duty_cycle)

# Servo steering range
SERVO_MIN = 230
SERVO_MAX = 500

# rolling buffer definition:
ROLLING_BUFFER_SIZE = 10
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


# this function plots an image with the detected contours in it.
def plot_nicely(img, roi_start, roi_height, contours, center, color):
    if img is None:
        print("Error: no img was passed")
        return
    
    x_dim, y_dim = img.shape
    scale =2.5
    x_dim_plot=int(x_dim/scale)
    y_dim_plot=int(y_dim/scale)

    # convert greyscale into color for visualization
    img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    # shift the countours to match the image position
    shift_contour = [contour + [0,roi_start] for contour in contours]
    # draw the counrours on the image
    cv2.drawContours(img,shift_contour, -1,color,2)
    # circle 
    radius=3
    if center:
        cv2.circle(img,(center,int(roi_start+roi_height/2)),radius,color,10  )

    return img


# this function plots a single image, with color, scale, position
def single_plot(img,plot_name,scale,position):
    y_dim, x_dim = img.shape[:2]
    x_plot = int(x_dim/scale)
    y_plot = int(y_dim/scale)
    cv2.namedWindow(plot_name,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(plot_name,x_plot,y_plot)
    cv2.moveWindow(plot_name,position[0],position[1])
    cv2.imshow(plot_name,img)


def img_roi(img,roi,blurr_size):

    roi = cv2.GaussianBlur(roi,(blurr_size,blurr_size),0)
    avg = cv2.mean(roi)[0]
    (minv, maxv, _, _) = cv2.minMaxLoc(roi)

    return [avg,minv,maxv]

def filter_contour_area(contours,mina,maxa):

    # Filter contours by area for blue threshold with area printing
    filtered_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if mina <= area <= maxa:
            filtered_contours.append(cnt)

    return filtered_contours



# function for trackbar
def nothing(val):
    pass


# define main plot window
slider1_name = "sliderB"
slider2_name = "sliderG"
slider3_name = "sliderCR"
slider4_name = "sliderSat"

cv2.namedWindow("img", cv2.WINDOW_NORMAL)
cv2.createTrackbar(slider1_name, "img", 0, 100, nothing)
cv2.createTrackbar(slider2_name, "img", 0, 100, nothing)
cv2.createTrackbar(slider3_name, "img", 0, 100, nothing)
cv2.createTrackbar(slider4_name, "img", 0, 100, nothing)


sliderB=0
sliderG=0
sliderCR=0
sliderSat=0

weigthed_center=0
try:
    while True:
        
        ret, img = cam.read()

        # calculate roi
        roi_width =  int(width*1.0)
        roi_height = int(height*0.20)
        roi_start=int(height/100*60)

        # Calculate top-left and bottom-right corners of the rectangle
        #  and draw the rectangle
        top_left = (int((width - roi_width) // 2), roi_start)
        bottom_right = (top_left[0] + roi_width, top_left[1] + roi_height)
        cv2.rectangle(img, top_left, bottom_right, (0, 0, 0), 1)
        
        # estract RGB
        imgB,imgG,imgR = cv2.split(img)

        # Convert the image to HSV
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_sat = hsv_img[:, :, 1]

        # Convert the image to YCrCb
        ycrcb_img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        img_cr = ycrcb_img[:, :, 1]

        # calculate the rois and apply them to the images
        roiB    = imgB[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        roiG    = imgG[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        roiSat  = img_sat[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        roiCR   = img_cr[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        
        #blur and extract avg, min, max
        blur_filter = 25
        avgB,minB,maxB       = img_roi(imgB,roiB,blur_filter)
        avgG,minG,maxG       = img_roi(imgG,roiG,blur_filter)
        avgSat,minSat,maxSat = img_roi(img_sat,roiSat,blur_filter)
        avgCR,minCR,maxCR    = img_roi(img_cr,roiCR,blur_filter)
        

        # # threshold. define the thresholds considering the min max and avg. 
        Blue_thresh  = int(avgB* (1+(1*sliderB/100)) )
        Green_thresh = int(avgG* (1+(1*sliderG/100)) )
        Sat_thresh   = int(avgG* (1+(1*sliderSat/100)) )
        CR_thresh    = int(avgG* (1+(1*sliderCR/100)) )

        # print("Blue_thresh: ",Blue_thresh)
        # print("Green_thresh: ",Green_thresh)
        # print("Sat_thresh: ",Sat_thresh)
        # print("CR_thresh: ",CR_thresh)

        # apply the threshold in each channel
        _, Bt = cv2.threshold(roiB, Blue_thresh, 255, cv2.THRESH_BINARY )
        _, Gt = cv2.threshold(roiG, Green_thresh, 255, cv2.THRESH_BINARY )

        # detect the countours
        contoursB, _ = cv2.findContours(Bt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contoursG, _ = cv2.findContours(Gt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Define a minimum and maximum area threshold
        min_area = 200  # Adjust as needed
        max_area = 30000  # Adjust as needed

        # Filter contours by area for blue threshold with area printing
        filtered_contoursB = filter_contour_area(contoursB,min_area,max_area)

        # Filter contours by area for green threshold with area printing
        filtered_contoursG = filter_contour_area(contoursG,min_area,max_area)

        # trova i centroidi 
        centroidsB = calculate_centroid(filtered_contoursB)
        centroidsG = calculate_centroid(filtered_contoursG)

        # average position of the centroids that I find. 
        avgB_c=calculate_average_x(centroidsB)
        avgG_c=calculate_average_x(centroidsG)

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
            # weigthed_center = int( (centroG * 0.8 + centroB * 0)  )
        elif centroB:
            weigthed_center = centroB
        elif centroG:
            weigthed_center = centroG
        

        cv2.circle(img, (weigthed_center, int(roi_start+roi_height/2)), 3, (0, 0, 255), 10)


        if weigthed_center:
            angle_avg=rolling_buffer(buffer, weigthed_center, ROLLING_BUFFER_SIZE)
            servo_angle = int((angle_avg / width) * (SERVO_MAX - SERVO_MIN) + SERVO_MIN)
            PCA9685.set_channel_value(channel, servo_angle)

        

        # define main plot
        scale_img=1
        cv2.resizeWindow("img", int(width/scale_img), int(height/scale_img))
        cv2.moveWindow("img",0,0)
        sliderB = cv2.getTrackbarPos(slider1_name,"img")
        sliderG = cv2.getTrackbarPos(slider2_name,"img")
        sliderCR = cv2.getTrackbarPos(slider3_name,"img")
        sliderSat = cv2.getTrackbarPos(slider4_name,"img")
   
        

        cv2.imshow("img",img)


        # merge image with found contours
        imgG = plot_nicely(imgG,roi_start,roi_height,filtered_contoursG,centroG,(0,255,0))
        imgB = plot_nicely(imgB,roi_start,roi_height,filtered_contoursB,centroB,(255,0,0))

        
        # plot image with detected contours
        single_plot(imgB,"imgB",2.5,[1000,0])
        single_plot(imgG,"imgG",2.5,[1000,400])



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