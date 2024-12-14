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

def update_canny_threshold(val):
    global canny_threshold
    canny_threshold = val

# Check if the images folder exists
if not os.path.exists(images_folder):
    print(f"The folder {images_folder} does not exist.")
else:
    # Start from image "1" and go up
    image_number = 1

    threshold_value = 0  # Initial threshold value
    kernel_size = 11  # Initial kernel size
    canny_threshold = 10  # Initial Canny edge threshold

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

                # Define ROI as the bottom half of the image
                height, width = r_channel.shape
                roi = r_channel[height // 2:, :]

                # Apply GaussianBlur to smooth the image
                blurred_roi = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)

                # Apply Canny edge detection to find edges
                edges = cv2.Canny(blurred_roi, canny_threshold, canny_threshold * 2)

                # Overlay edges onto the red channel image
                r_with_edges = r_channel.copy()
                r_with_edges[height // 2:, :][edges > 0] = 255  # Highlight edges in white

                # Merge the red channel back into an RGB image
                r_with_roi = cv2.merge([r_with_edges, r_with_edges, r_with_edges])
                cv2.rectangle(r_with_roi, (0, height // 2), (width, height), (0, 255, 0), 2)

                # Add sliders to the displayed image
                def nothing(x):
                    pass

                cv2.namedWindow("Red Channel with Edges", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Red Channel with Edges", 800, 600)  # Resize window to smaller dimensions
                cv2.createTrackbar("Threshold", "Red Channel with Edges", threshold_value, 255, update_threshold)
                cv2.createTrackbar("Kernel Size", "Red Channel with Edges", kernel_size, 21, update_kernel_size)
                cv2.createTrackbar("Canny Thresh", "Red Channel with Edges", canny_threshold, 255, update_canny_threshold)

                # Display the red channel with edges in the ROI
                cv2.imshow("Red Channel with Edges", r_with_roi)

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
