import cv2
import os
import matplotlib.pyplot as plt


def plot_rgb(img,y_pos,id):

    boola=True
    
    b,g,r = cv2.split(img)
    x_dim,y_dim,ch= img.shape
    scale = 2.7
    y_dim_plot = int(x_dim/scale)
    x_dim_plot = int(y_dim/scale)



    cv2.namedWindow(f"img {id}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"img {id}", x_dim_plot, y_dim_plot)
    cv2.imshow(f"img {id}", img)
    # red img
    cv2.namedWindow(f"R {id}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"R {id}", x_dim_plot, y_dim_plot)
    cv2.imshow(f"R {id}", r)
    # green img
    cv2.namedWindow(f"G {id}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"G {id}", x_dim_plot, y_dim_plot)
    cv2.imshow(f"G {id}", g)
    # blu img
    cv2.namedWindow(f"B {id}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"B {id}", x_dim_plot, y_dim_plot)
    cv2.imshow(f"B {id}", b)

    if boola==True:
        cv2.moveWindow(f"B {id}", x_dim_plot*3, y_pos)
        cv2.moveWindow(f"G {id}", x_dim_plot*2, y_pos)
        cv2.moveWindow(f"R {id}", x_dim_plot*1, y_pos)
        cv2.moveWindow(f"img {id}", x_dim_plot*0, y_pos)
    else:
        boola=False



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



def merge_thresh_image(img,threshold,top,height,width):

    # Create a copy of the original image to overlay the thresholded ROI
    output_image = img.copy()   # Convert to BGR to display color
    output_image[top:top+height, 0:width] = threshold  # Update the blue channel

    return output_image


def calculate_average_x(centroids):
    if len(centroids) == 0:
        print("No centroids to calculate the average.")
        return None
    total_x = sum(cx for cx, cy in centroids)
    average_x = total_x / len(centroids)
    return int(average_x)



def go(path, display_time):
    
    global centroB
    global centroG
    global weigthed_center

    if not os.path.exists(path):
        print(f"The path {path} does not exist.")
        return

    # Get all image files in the directory sorted by name
    images = sorted(os.listdir(path))

    for i in range(len(images)):
        img_name = f"{i}.jpg"
        img_full_path = os.path.join(path, img_name)

        # Skip if it's not an image file
        if not img_name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
            continue

        img = cv2.imread(img_full_path)


        if img is None:
            print(f"Unable to load image: {img_full_path}")
            continue
        
        height,width,ch= img.shape

        # print("image shape: h: ",height," w: ",width)


        # Calculate ROI dimensions
        roi_width = int(width * 1.0)  # 100% of the image width
        roi_height = int(height * 0.15)  # 15% of the image height

        roi_start=int(height/100*65)

        # Calculate top-left and bottom-right corners of the rectangle
        top_left = (int((width - roi_width) // 2), roi_start)
        # print(f"top_left: {top_left}")
        bottom_right = (top_left[0] + roi_width, top_left[1] + roi_height)
        # print(f"bottom_right: {bottom_right}")

        # Draw the rectangle (blue color, thickness 2)
        cv2.rectangle(img, top_left, bottom_right, (0, 0, 0), 1)

        # split the image into BGR. 
        imgB,imgG,imgR = cv2.split(img)

        # define the rois
        roiB = imgB[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        roiG = imgG[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]



        # blurra le roi dei canali
        filter_size=25
        roiB = cv2.GaussianBlur(roiB,(filter_size,filter_size),0)
        roiG = cv2.GaussianBlur(roiG,(filter_size,filter_size),0)

        # Calculate the average color in each channel (BGR format)
        avgB = cv2.mean(roiB)[0]
        avgG = cv2.mean(roiG)[0]
        # avgR = cv2.mean(roiR)[0]
        # print(f"*avgB: {avgB} *avgG: {avgG} ")
        # max min
        (minValB, maxValB, _, _) = cv2.minMaxLoc(roiB)
        (minValG, maxValG, _, _) = cv2.minMaxLoc(roiG)
        # show this stuff
        # print(f"*maxValB: {maxValB} *maxValG: {maxValG} ")
        # print(f"*minValB: {minValB} *minValG: {minValG} ")

        


        # threshold. define the thresholds considering the min max and avg. 

        Blue_thresh  = max (100,int(avgB*1.3))
        Green_thresh = max(20,int(avgG*3))

        # probably there is no line in the image. do not detect a line
        
        if((maxValB-minValB)<50):
            Blue_thresh=255
        
        if((maxValG-minValG)<20):
            Green_thresh=255


        # Apply Otsu's Thresholding for each channel
        _, Bt = cv2.threshold(roiB, Blue_thresh, 255, cv2.THRESH_BINARY )
        _, Gt = cv2.threshold(roiG, Green_thresh, 255, cv2.THRESH_BINARY )


        # Detect contours for the blue threshold
        contoursB, _ = cv2.findContours(Bt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Detect contours for the green threshold
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

        scale_img=1
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("img", int(width/scale_img), int(height/scale_img))
        cv2.moveWindow("img",0,0)
        cv2.imshow("img",img)
        
        
        # plot the 2 images together. 
        plot_two2(imgG,imgB,roi_start,roi_height,filtered_contoursG,filtered_contoursB,centroB,centroG,scale_img)


        # Wait for the specified time or until 'q' is pressed
        key = cv2.waitKey(int(display_time*100)) & 0xFF

        if key == ord('q'):
            print("Exiting...")
            break
        elif key == ord('s'):
            display_time *= 2
        elif key == ord('f'):
            display_time /= 2


            

    # Destroy all OpenCV windows after exiting the loop
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Path to the calibration image
    calib_path = "./imgs_saved/imgs1/calib.jpg"

    centroB=0
    centroG=0
    weigthed_center=0

    # Path to the directory containing images
    path = "./imgs_saved/imgs1/"
    go(path, 0.1)
