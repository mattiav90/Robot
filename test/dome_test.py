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
    kernel_size = 7  # Initial kernel size
    canny_threshold_min = 10  # Initial Canny edge threshold
    canny_threshold_max = 80  # Initial Canny edge threshold

    # 70% down in the image to 80%. ROI position
    ROI_scale = 70
    ROI_scale_bottom = 80
    closing = 40

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

                # Calculate the average gray value of the ROI
                avg_gray_value = np.mean(roi)
                print(f"Average gray value of ROI: {avg_gray_value:.2f}")

                # Apply Canny edge detection to find edges
                edges = cv2.Canny(roi, canny_threshold_min, canny_threshold_max)

                # Define the dimensions of the rectangle
                rect_width = 100  # Width of the rectangle
                rect_height = 50  # Height of the rectangle

                # Draw the black rectangle in the bottom-left corner
                cv2.rectangle(edges, (0, height - rect_height), (rect_width, height), (255, 255, 0), -1)

                # Perform morphological closing to connect edges
                kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (closing, closing))
                closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel1)

                # Find contours of the closed edges
                contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Filter out small contours and those near the bottom edges
                min_contour_area = 200  # Minimum area threshold
                max_contour_area = width * height / 6  # Maximum area threshold
                filtered_contours = []
                for cnt in contours:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        area = cv2.contourArea(cnt)
                        if area >= min_contour_area and area < max_contour_area and cy < (height - 600):  # Exclude contours near the bottom
                            filtered_contours.append(cnt)

                # Draw all contours in blue
                r_with_edges = cv2.merge([r_channel, r_channel, r_channel])
                roi_overlay = r_with_edges[ ROI_scale * height // 100 :ROI_scale_bottom * height // 100 , :]
                cv2.drawContours(roi_overlay, contours, -1, (255, 0, 0), thickness=2)  # Blue for all contours

                # Draw filtered contours in green
                cv2.drawContours(roi_overlay, filtered_contours, -1, (0, 255, 0), thickness=2)  # Green for filtered contours

                # Merge the red channel back into an RGB image
                cv2.rectangle(r_with_edges, (0, ROI_scale * height // 100 ), (width,  ROI_scale_bottom * height // 100), (0, 255, 0), 2)

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
                cv2.imshow("Red Channel with Edges", r_with_edges)
                # cv2.imshow("Red Channel with Edges", edges)
                # cv2.imshow("Red Channel with Edges", edges)

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
