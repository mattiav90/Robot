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

def update_blur_kernel(val):
    global blur_kernel_size
    blur_kernel_size = max(1, val | 1)  # Ensure kernel size is always odd

# Check if the images folder exists
if not os.path.exists(images_folder):
    print(f"The folder {images_folder} does not exist.")
else:
    # Start from image "1" and go up
    image_number = 1

    # Initial slider values
    threshold_value = 0
    kernel_size = 3
    canny_threshold_min = 10
    canny_threshold_max = 20
    blur_kernel_size = 13  # Initial blur kernel size

    # ROI parameters
    ROI_scale = 70
    ROI_scale_bottom = 85
    min_length = 20  # Minimum contour length for filtering
    max_length = 1000  # Maximum contour length for filtering

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

                # Define ROI
                height, width = r_channel.shape
                roi = r_channel[ROI_scale * height // 100:ROI_scale_bottom * height // 100, :]

                # Apply Gaussian Blur to reduce noise
                blurred_roi = cv2.GaussianBlur(roi, (blur_kernel_size, blur_kernel_size), 0)

                # Update kernels dynamically based on the trackbar
                kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
                kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 30))

                # Apply Canny edge detection
                edges = cv2.Canny(blurred_roi, canny_threshold_min, canny_threshold_max)

                # Perform morphological closing to connect edges
                closed_edges = cv2.dilate(edges, kernel1, iterations=1)
                closed_edges = cv2.morphologyEx(closed_edges, cv2.MORPH_CLOSE, kernel2)

                # Find contours of the closed edges
                contours_edge, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Filter contours by length
                filtered_contours = []
                for contour in contours_edge:
                    length = cv2.arcLength(contour, closed=True)
                    if min_length <= length <= max_length:
                        filtered_contours.append(contour)

                # Create an RGB image from the red channel
                r_with_edges = cv2.merge([r_channel, r_channel, r_channel])
                roi_overlay = r_with_edges[ROI_scale * height // 100:ROI_scale_bottom * height // 100, :]

                # Draw filtered contours
                cv2.drawContours(roi_overlay, filtered_contours, -1, (0, 255, 0), thickness=2)

                # Draw ROI rectangle
                cv2.rectangle(r_with_edges, (0, ROI_scale * height // 100),
                              (width, ROI_scale_bottom * height // 100), (0, 0, 255), 2)

                # Create a window with trackbars
                cv2.namedWindow("Red Channel with Edges", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Red Channel with Edges", 800, 600)
                cv2.createTrackbar("Threshold", "Red Channel with Edges", threshold_value, 255, update_threshold)
                cv2.createTrackbar("Kernel Size", "Red Channel with Edges", kernel_size, 21, update_kernel_size)
                cv2.createTrackbar("Canny Thresh min", "Red Channel with Edges", canny_threshold_min, 255,
                                   update_canny_threshold_min)
                cv2.createTrackbar("Canny Thresh max", "Red Channel with Edges", canny_threshold_max, 255,
                                   update_canny_threshold_max)
                cv2.createTrackbar("Blur Kernel Size", "Red Channel with Edges", blur_kernel_size, 21, update_blur_kernel)

                # Display the image
                cv2.imshow("Red Channel with Edges", r_with_edges)
                key = cv2.waitKey(30)

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
