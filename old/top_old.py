import cv2
import numpy as np
import time
# for steering
import Fabo_PCA9685
import pkg_resources
import smbus
#back motors
import RPi.GPIO as GPIO
import os


# activate the back motors
os.system("sudo busybox devmem 0x6000d504 32 0x2")
os.system("sudo busybox devmem 0x700031fc 32 0x45")
os.system("sudo busybox devmem 0x70003248 32 0x46")
os.system("sudo busybox devmem 0x6000d100 32 0x00")



# initialize the servo
BUSNUM=1
SERVO_HZ=50
INITIAL_VALUE=300
bus = smbus.SMBus(BUSNUM)
PCA9685 = Fabo_PCA9685.PCA9685(bus,INITIAL_VALUE)
PCA9685.set_hz(SERVO_HZ)
# this is the single channel of BUS0. 
channel=0

# steering extremities
start=230
end=500


#activate back motors

# Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)

# Start PWM
my_pwm1 = GPIO.PWM(32, 100)  # 100 Hz
my_pwm2 = GPIO.PWM(33, 100)  # 100 Hz
duty_cycle = 50 # Initial duty cycle (10%)
my_pwm1.start(duty_cycle)
my_pwm2.start(duty_cycle)


# window width and height
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
# cv2.namedWindow('cam1')
cv2.namedWindow('cam2')
# positions of windows
cv2.moveWindow('cam', 0, 0)
# cv2.moveWindow('cam1', 500, 0)
cv2.moveWindow('cam2', 500, 500)


cv2.createTrackbar('x1', 'cam', 100, 200, nothing)
cv2.createTrackbar('x2', 'cam', 250, 500, nothing)
# cv2.createTrackbar('x3', 'cam', 100, 500, nothing)
# cv2.createTrackbar('x4', 'cam', 255, 500, nothing)

# Set a minimum area for contours to be considered "big"
min_area = 70  # You can adjust this value as needed


# kernels
dim_s=5
kernel_soft=np.ones((dim_s,dim_s),np.float32)/20
dim_m=15
kernel_medium =np.ones((dim_m,dim_m),np.float32)/5
dim=30
kernel_hard=np.ones((dim,dim),np.float32)/2


while True:
    # Grab image
    ret, img = cam.read()
    if not ret:
        break

    
    x1 = cv2.getTrackbarPos('x1', 'cam')
    x2 = cv2.getTrackbarPos('x2', 'cam')
    # x3 = cv2.getTrackbarPos('x3', 'cam')
    # x4 = cv2.getTrackbarPos('x4', 'cam')
    

    # Get dimensions
    height, width, _ = img.shape
    
    # Define the ROI (bottom half)
    roi_start_y = height // 2
    roi_end_y = height
    img = img[roi_start_y:roi_end_y, 0:width]  # Slicing to get the bottom half
    # re set based on the new shape
    height, width, _ = img.shape
    # print("image height: ",height," width: ",width)

    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    # cv2.imshow("HSV",hsv)

    # [H,S,V]=cv2.split(hsv)

    # for (name,chan) in zip(("H","S","V"), cv2.split(hsv)):
    #     cv2.imshow(name,chan)
    
    
    #convert in grey scale
    grey= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # grey=V
    # cv2.imshow("grigio",grey)



    # blur a littlebit the image
    dst=cv2.filter2D(grey,-1,kernel_soft)

    #get the average grey  (returns an rgb space. use only the first value)
    avg = cv2.mean(dst)
    avg= avg[0]*(x1/100)*0.8        #this is just (avg*1).
    print("avg= ",avg)

    # Step 1: Threshold the image
    _, thresh1 = cv2.threshold(dst, avg, 255, cv2.THRESH_BINARY)
    thresh1= cv2.bitwise_not(thresh1)
    # erode
    thresh1= cv2.erode(thresh1,kernel_medium,iterations = 1)
    
    # dilate
    # thresh1=cv2.dilate(thresh1,kernel_medium)

    # Step 3: Find contours
    contours, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Step 4: Approximate the contours
    approx_contours = [cv2.approxPolyDP(c, 0.001 * cv2.arcLength(c, True), True) for c in contours]

    x=0
    # Optionally, draw the approximated contours on the original image
    for c in approx_contours:
        cv2.drawContours(img, [c], -1, (255, 0, 0), 2) 

        x,y,w,h = cv2.boundingRect(c)
        aspect_ratio = float(w)/h
        area=cv2.contourArea(c)
        # if (aspect_ratio<0.6) and area>1000:
        if  (aspect_ratio<0.6) and area>2000:
            cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
            angle=((x/width)*(end-start) )+start
            PCA9685.set_channel_value(channel,angle)
            print("area: ",area," aspect_ratio: ",aspect_ratio)

        #     (x,y),(MA,ma),angle = cv2.fitEllipse(c)
        #     ratio=ma/MA
        #     # print("MA: ",MA," ma: ",ma," ratio: ",ratio)
        #     test_feature=int(height-200)

        #     # controls if the height of the enclosing rectangle is close to the
        #     # entire height of the image
        #     test_height = (height-h)< 100 

        #     # if ratio>int(10) and test_height:
        #     if ratio>int(2) :
        #         cv2.drawContours(img, [c], -1, (0, 255, 0), 2) 
        #         rect_area=w*h
        #         extent=float(area)/rect_area
        #         # print("extent: ",extent)     
        #         # print("ratio: ",ratio)
        #         # print("angle: ",angle)     
        #         # print("rece height: ",h," w: ",w)   
        #         print("area: ",area," aspect_ratio: ",aspect_ratio," h: ",h," ratio: ",ratio)

                
        #         # Calculate the centroid coordinates
        #         M = cv2.moments(c)
        #         x = int(M['m10'] / M['m00'])
        #         y = int(M['m01'] / M['m00'])
        #         print("x: ",x)
        #         angle=((x/width)*(end-start) )+start
        #         PCA9685.set_channel_value(channel,angle)

                




    # Display the original image with the edge-detected ROI
    cv2.imshow('cam', img)
    # cv2.imshow('cam1', contours)
    cv2.imshow('cam2', thresh1)
    
    

    if cv2.waitKey(1) == ord('q'):
        break


# Cleanup

# close the cam
cam.release()
cv2.destroyAllWindows()

# stop pwm
my_pwm1.stop()
my_pwm2.stop()
GPIO.cleanup()



# histogram 

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
