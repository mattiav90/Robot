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



def plot_two2(imgG, imgB, roi_start, roi_height, contoursG, contoursB):
    if imgG is None or imgB is None:
        print("Error: One or both images are invalid.")
        return

    x_dim, y_dim = imgG.shape
    scale = 2
    x_dim_plot = int(x_dim / scale)
    y_dim_plot = int(y_dim / scale)
    print("x_dim_plot:", x_dim_plot, "y_dim_plot:", y_dim_plot)

    # Convert grayscale images to BGR for visualization
    imgG = cv2.cvtColor(imgG, cv2.COLOR_GRAY2BGR)
    imgB = cv2.cvtColor(imgB, cv2.COLOR_GRAY2BGR)

    # Translate contours by applying an offset to the y-coordinate
    translated_contoursB = [contour + [0, roi_start] for contour in contoursB]
    translated_contoursG = [contour + [0, roi_start] for contour in contoursG]

    # Draw translated contours on the images
    cv2.drawContours(imgB, translated_contoursB, -1, (255, 0, 0), 2)
    cv2.drawContours(imgG, translated_contoursG, -1, (0, 255, 0), 2)

    # Create named windows for resizing
    cv2.namedWindow("imgB", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("imgB", y_dim_plot, x_dim_plot)
    cv2.moveWindow("imgB",0,0)
    cv2.imshow("imgB", imgB)

    cv2.namedWindow("imgG", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("imgG", y_dim_plot, x_dim_plot)
    cv2.moveWindow("imgG",int(y_dim_plot*1.15),0)
    cv2.imshow("imgG", imgG)





def merge_thresh_image(img,threshold,top,height,width):

    # Create a copy of the original image to overlay the thresholded ROI
    output_image = img.copy()   # Convert to BGR to display color
    output_image[top:top+height, 0:width] = threshold  # Update the blue channel

    return output_image




def load_img(path, display_time):
    """
    Load and display images from the specified directory after subtracting a calibration image.

    Args:
        path (str): Path to the directory containing images.
        display_time (float): Time in seconds to display each image.
        calib_img (ndarray): The calibration image to subtract from each image.
    """
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
        roi_height = int(height * 0.10)  # 15% of the image height

        roi_start=int(height/100*70)

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
        print(f"*avgB: {avgB} *avgG: {avgG} ")
        # max min
        (minValB, maxValB, _, _) = cv2.minMaxLoc(roiB)
        (minValG, maxValG, _, _) = cv2.minMaxLoc(roiG)
        # show this stuff
        print(f"*maxValB: {maxValB} *maxValG: {maxValG} ")
        print(f"*minValB: {minValB} *minValG: {minValG} ")
        

        


        # threshold. define the thresholds considering the min max and avg. 

        Blue_thresh  = max (100,int(avgB*1.25))
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




        # plot the 2 images together. 
        plot_two2(imgG,imgB,roi_start,roi_height,contoursG,contoursB)





        # Wait for the specified time or until 'q' is pressed
        if cv2.waitKey(int(display_time * 1000)) & 0xFF == ord('q'):
            print("Exiting...")
            break

    # Destroy all OpenCV windows after exiting the loop
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Path to the calibration image
    calib_path = "./imgs_saved/imgs1/calib.jpg"

    # Path to the directory containing images
    path = "./imgs_saved/imgs1/"
    load_img(path, 0.01)
