import RPi.GPIO as GPIO
import time
import os
import Fabo_PCA9685
import pkg_resources
import smbus
import argparse
import cv2
from collections import deque
from builtins import open



# **************************** main variables of script ****************************

thresh_save_G   = 50
thresh_save_Sat = 60

enable_G   = True
enable_Sat = True

# contours filtering
min_area = 500
max_area = 30000  

# robot speed
speed = 0

# ************************************************************************************
#  image dimensions (do not change)
width=1100
height=800

# roi position:
roi_height = int(height*0.20)
roi_start  = int(height/100*65)

# ************************************************************************************

roi_width  = int(width*1.0)


assert any([ enable_G, enable_Sat]), "Error: At least one of the controls must be active!"

def rolling_buffer(buffer, value, size):
    if len(buffer) == size:
        buffer.popleft()
    buffer.append(value)
    return sum(buffer) / len(buffer)


# set up the camera

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

my_pwm1.start(speed)

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
def single_plot(img,plot_name,scale,position,enable):
    y_dim, x_dim = img.shape[:2]
    x_plot = int(x_dim/scale)
    y_plot = int(y_dim/scale)

    if enable:
        color_dot=(0,255,0)
    else:
        color_dot=(0,0,255)

    cv2.namedWindow(plot_name,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(plot_name,x_plot,y_plot)
    cv2.moveWindow(plot_name,position[0],position[1])
    cv2.circle(img,(20,20),3,color_dot,20)
    cv2.imshow(plot_name,img)



def img_roi(img,blurr_size):

    roi = cv2.GaussianBlur(img,(blurr_size,blurr_size),0)
    avg = cv2.mean(img)[0]
    (minv, maxv, _, _) = cv2.minMaxLoc(img)

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


def check_if_exist(val):
    out=0
    if val:
        out=val
    else:
        out=None
    return out

def print4(val1,val2,val3,val4):
    print(f"val1: {val1} val2: {val2} val3: {val3} val4: {val4}")
    return 0




class Final_center:
    def __init__(self):
        self.Lastavg=0
        self.avg=0
    
    def center(self,centers,enable):

        valid=0
        for i, center in enumerate(centers):    
            if enable[i]!=False and centers[i]!=None:
                valid+=1
            else:
                centers[i]=None
        
        avg=0
        for i in range(len(centers)):
            if enable[i]!=False and centers[i]!=None:
                avg=avg+centers[i]

        if valid==0:
            avg=self.Lastavg
        else:
            avg=avg/valid
            self.Lastavg=avg
        
        return int(avg)




class Rolling_buffer:
    def __init__(self,size):
        self.size=size
        self.buffer=[]
        self.lastNumerical=0

    def append(self,val):
        if len(self.buffer)==self.size:
            self.buffer.pop(0)
        self.buffer.append(val)
    
    def avg(self):
        if not self.buffer:
            return 0

        avg = int(sum(self.buffer)/len(self.buffer))

        if avg!=None:
            self.lastNumerical=avg
        else:
            avg=lastNumerical
        

        print("buffer: ",self.buffer," avg: ",avg)
        
        return avg



def go(sim,idx,plot):

    buffer_width=4
    RB = Rolling_buffer(buffer_width)

    FC = Final_center()

    # define main plot window and trackbars in it.
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.moveWindow("img",0,500)
    slider2_name = "sliderG"
    slider4_name = "sliderSat"
    cv2.createTrackbar("sliderG", "img", thresh_save_G, 100, nothing)
    cv2.createTrackbar("sliderSat", "img", thresh_save_Sat, 100, nothing)
    sliderG=0
    sliderSat=0

    print("sim: ",sim)


    path = "imgs_saved/all/"
    images = sorted(os.listdir(path))

    pause=False
    weigthed_center=0
    i=0
    try:
        while True:

            # if I want to run a simulation
            if args.sim:
                i+=1
                if i==len(images)-1:
                    i=1
                img_name=f"{i+1}.jpg"
                if idx!=False:
                    img_name=f"{idx}.jpg"
                full_path = os.path.join(path,img_name)
                try:
                    img=cv2.imread(full_path)
                except:
                    pass
            
            # if it is using the cam
            else:
                ret, img = cam.read()

            # Calculate top-left and bottom-right corners of the rectangle
            #  and draw the rectangle
            top_left = (int((width - roi_width) // 2), roi_start)
            bottom_right = (top_left[0] + roi_width, top_left[1] + roi_height)
            # cv2.rectangle(img, top_left, bottom_right, (0, 0, 0), 1)
            
            # Crop the image before conversion
            cropped_img = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            
            # estract RGB
            _,imgG,_ = cv2.split(cropped_img)

            # Convert the image to HSV
            hsv_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2HSV)
            imgSat = hsv_img[:, :, 1]
            imgSat = 255-imgSat


            # calculate the rois and apply them to the images
            # roiG    = imgG[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            # roiSat  = imgSat[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            
            #blur and extract avg, min, max
            blur_filter = 25
            avgG,_,_       = img_roi(imgG,blur_filter)
            avgSat,minSat,maxSat = img_roi(imgSat,blur_filter)



            # print4(avgB,avgG,avgSat,avgCR)
            

            # # threshold. define the thresholds considering the min max and avg. 
            Green_thresh = int(avgG*   (1+(10*sliderG/100)) )
            Sat_thresh   = int(avgSat* (1+(10*sliderSat/100)) )

            print(f" Green_thresh: {Green_thresh} Sat_thresh: {Sat_thresh} ")

            # print4(Blue_thresh,Green_thresh,Sat_thresh,CR_thresh)


            # apply the threshold in each channel
            _, Gt   = cv2.threshold(imgG,   Green_thresh, 255, cv2.THRESH_BINARY )
            _, Satt = cv2.threshold(imgSat, Sat_thresh, 255, cv2.THRESH_BINARY )

            # detect the countours
            contoursG, _   = cv2.findContours(Gt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contoursSat, _ = cv2.findContours(Satt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


            # Filter contours by area for blue threshold with area printing
            filtered_contoursG   = filter_contour_area(contoursG,min_area,max_area)
            filtered_contoursSat = filter_contour_area(contoursSat,min_area,max_area)



            # trova i centroidi 
            centroidsG   = calculate_centroid(filtered_contoursG)
            centroidsSat = calculate_centroid(filtered_contoursSat)

            # print4(centroidsB,centroidsG,centroidsSat,centroidsCR)

            # average position of the centroids that I find. 
            avgG_c=calculate_average_x(centroidsG)
            avgSat_c=calculate_average_x(centroidsSat)

            # print4(avgB_c,avgG_c,avgSat_c,avgCR_c)

            # modify the global centro variables if something has been detected
            centroG = check_if_exist(avgG_c)
            centroSat = check_if_exist(avgSat_c)

            # print("centroB: ",centroB," centroG: ",centroG," centroSat: ",centroSat," centroCR: ",centroCR )
            
            # calculating the weighted center across all the selected controls
            weigthed_center = FC.center([centroG,centroSat],[enable_G,enable_Sat])


            
            if weigthed_center:
                RB.append(weigthed_center)
            
            # calcualte avg of values
            avg_center= RB.avg()
            cv2.circle(img, (avg_center, int(roi_start+roi_height/2)), 3, (0, 0, 255), 10)
            angle_avg=rolling_buffer(buffer, avg_center, ROLLING_BUFFER_SIZE)
            servo_angle = int((angle_avg / width) * (SERVO_MAX - SERVO_MIN) + SERVO_MIN)
            PCA9685.set_channel_value(channel, servo_angle)
                
            

            # define main plot
            scale_img=1.5
            cv2.resizeWindow("img", int(width/scale_img), int(height/scale_img))
            sliderG = cv2.getTrackbarPos(slider2_name,"img")
            sliderSat = cv2.getTrackbarPos(slider4_name,"img")

            cv2.imshow("img",img)


            if plot:
                # merge image with found contours
                # imgB   = plot_nicely(imgB,roi_start,roi_height,filtered_contoursB,centroB,(255,0,0))
                imgG   = plot_nicely(imgG,roi_start,roi_height,filtered_contoursG,centroG,(255,0,0))
                imgSat = plot_nicely(imgSat,roi_start,roi_height,filtered_contoursSat,centroSat,(0,0,255))

                scale_subplot=3.3
                offset=int(width/scale_subplot)
                allign=100
                # plot image with detected contours
                single_plot(imgG,"imgG",scale_subplot     ,[allign+offset*1,0] , enable_G   )
                single_plot(imgSat,"imgSat",scale_subplot ,[allign+offset*2,0] , enable_Sat )


            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): #quit
                break
            elif key == ord('p') and args.sim==True:    #pause
                pause = not pause
            
            # pause mode
            while pause:
                key = cv2.waitKey(1) & 0xFF 
                if key == ord('p'):  
                    pause = False




    # closing up everything
    finally:
        print("Cleaning up resources...")
        my_pwm1.stop()
        my_pwm2.stop()
        GPIO.cleanup()
        cam.release()
        cv2.destroyAllWindows()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulation=<bool>")
    parser.add_argument("--sim", type=bool, help="Enable simulation mode.",default=False)
    parser.add_argument("--idx", type=int, help="Fix the loaded image",default=False)
    parser.add_argument("--plot", type=bool, help="print all the control images", default=False )
    args = parser.parse_args()

    if args.sim:
        print("Simulation run")
        args.plot=True
    else:
        print("Real run")
        


    # launch the main function
    go(args.sim,args.idx,args.plot)

