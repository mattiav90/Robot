import os
import cv2
import numpy as np

# Define the root folder and the images folder
root_folder = "/home/mattiav90/Desktop/Robot"  # Replace with the actual path to the root folder
images_folder = os.path.join(root_folder, "imgs_saved/dome/1")  # Replace "images" with the name of your images folder

# Define callback functions for the trackbars
def update_threshold(val):
    global threshold_value
    threshold_value = val

def update_kernel_size(val):
    global kernel_size
    kernel_size = max(1, val | 1)  # Ensure kernel size is always odd

def update_canny_threshold_min(val):
    global canny_threshold_min
    canny_threshold_min = val

def update_canny_threshold_max(val):
    global canny_threshold_max
    canny_threshold_max = val

# Check if the images folder exists
if not os.path.exists(images_folder):
    print(f"The folder {images_folder} does not exist.")
else:
    # Start from image "1" and go up
    image_number = 1

    threshold_value = 0  # Initial threshold value
    kernel_size = 30  # Initial kernel size
    canny_threshold_min = 30  # Initial Canny edge threshold
    canny_threshold_max = 90  # Initial Canny edge threshold

    # 70% down in the image to 80%. ROI position
    ROI_scale = 70
    ROI_scale_bottom = 85
    closing = 3

    kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size,kernel_size))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size+20,kernel_size+20))


    while True:
        filename = f"{image_number}.jpg"  # Assuming images are named as numbers with .jpg extension
        file_path = os.path.join(images_folder, filename)

        # Check if the image file exists
        if os.path.isfile(file_path):
            print(f"Displaying image: {filename}")
            try:
                img = cv2.imread(file_path)

                # Extract the red channel
                _, _, r_channel = cv2.split(img)

                # Define ROI with left corner same position, bottom corner higher
                height, width = r_channel.shape
                roi = r_channel[ ROI_scale * height // 100 :ROI_scale_bottom * height // 100 , :]

                # ***************************** start with threshold *****************************

                ycrcb_img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
                cr_channel = ycrcb_img[:, :, 1]

                # Define ROI as the bottom third of the image
                roi_cr = cr_channel[ ROI_scale * height // 100 :ROI_scale_bottom * height // 100 , :]

                # Calculate the average gray value in the Cr channel ROI
                avg_cr_value = np.mean(roi_cr)
                print("Average gray value in Cr channel (ROI): ",avg_cr_value*0.91," ")

                # Apply threshold on the Cr channel
                thresholded_saturation = cv2.inRange(roi_cr, 10, int(avg_cr_value)*0.91)

                closed_thresh = cv2.dilate(thresholded_saturation, kernel1, iterations=1)

                closed_thresh, _ = cv2.findContours(thresholded_saturation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
               
                
                # ***************************** now do it with edge detection *****************************

                # Apply Canny edge detection to find edges
                edges = cv2.Canny(roi, canny_threshold_min, canny_threshold_max)


                # Perform morphological closing to connect edges
                closed_edges = cv2.dilate(edges, kernel1, iterations=1)

                closed_edges = cv2.morphologyEx(closed_edges, cv2.MORPH_CLOSE, kernel2)

                # Find contours of the closed edges
                contours_edge, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

   
                # ***************************** calculate intersection *****************************
                # Step 1: Create binary masks for both contour sets
                mask_thresh = np.zeros((height, width), dtype=np.uint8)
                cv2.drawContours(mask_thresh, closed_thresh, -1, 255, thickness=cv2.FILLED)  # Fill the contours from closed_thresh

                mask_edges = np.zeros((height, width), dtype=np.uint8)
                cv2.drawContours(mask_edges, contours_edge, -1, 255, thickness=cv2.FILLED)  # Fill the contours from contours

                # Step 2: Perform a logical AND operation
                intersection_mask = cv2.bitwise_and(mask_thresh, mask_edges)

                intersection_mask = cv2.dilate(intersection_mask, kernel2, iterations=1)


                # Step 3: Extract contours from the intersection mask
                intersected_contours, _ = cv2.findContours(intersection_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)



                # # Filter out small contours and those near the bottom edges
                # min_contour_area = 100  # Minimum area threshold
                # max_contour_area = width * height / 6  # Maximum area threshold
                # filtered_contours = []
                # for cnt in intersected_contours:
                #     area = cv2.contourArea(cnt)
                #     if area >= min_contour_area :  
                #         filtered_contours.append(cnt)



                # Draw all contours in blue
                r_with_edges = cv2.merge([cr_channel, cr_channel, cr_channel])
                roi_overlay = r_with_edges[ ROI_scale * height // 100 :ROI_scale_bottom * height // 100 , :]

                # Draw filtered contours in green
                cv2.drawContours(roi_overlay, contours_edge, -1, (0, 255, 0), thickness=2)  # Green for filtered contours

                # Draw thresholded contours in red
                cv2.drawContours(roi_overlay, closed_thresh, -1, (255, 0, 0), thickness=2)  # Red for filtered contours

                # Step 4: Draw the intersected contours in red
                cv2.drawContours(roi_overlay, intersected_contours, -1, (0, 0, 255), thickness=2)  # Red for intersected contours

                # Merge the red channel back into an RGB image
                cv2.rectangle(r_with_edges, (0, ROI_scale * height // 100 ), (width,  ROI_scale_bottom * height // 100), (0, 0, 0), 2)

                # Add sliders to the displayed image
                def nothing(x):
                    pass

                cv2.namedWindow("Red Channel with Edges", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Red Channel with Edges", 800, 600)  # Resize window to smaller dimensions
                cv2.createTrackbar("Threshold", "Red Channel with Edges", threshold_value, 255, update_threshold)
                cv2.createTrackbar("Kernel Size", "Red Channel with Edges", kernel_size, 21, update_kernel_size)
                cv2.createTrackbar("Canny Thresh min", "Red Channel with Edges", canny_threshold_min, 255, update_canny_threshold_min)
                cv2.createTrackbar("Canny Thresh max", "Red Channel with Edges", canny_threshold_max, 255, update_canny_threshold_max)

                # Display the red channel with edges and contours in the ROI
                cv2.imshow("Red Channel with Edges", roi_overlay)
                # cv2.imshow("Red Channel with Edges", closed_edges)

                key = cv2.waitKey(30)  # Display image for 0.5 seconds

                # If 'q' is pressed, exit the loop
                if key == ord('q'):
                    print("Exiting...")
                    break

            except Exception as e:
                print(f"Could not process image {filename}: {e}")

        else:
            print(f"Image {filename} not found. Ending loop.")
            break

        image_number += 1

    cv2.destroyAllWindows()
