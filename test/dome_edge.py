import os
import cv2
import numpy as np
from collections import deque


# Define the root folder and the images folder
root_folder = "/home/mattiav90/Desktop/Robot"  # Replace with the actual path to the root folder
images_folder = os.path.join(root_folder, "imgs_saved/no_dome/1")  # Replace "images" with the name of your images folder



class RollingBuffer:
    def __init__(self, size):
        self.size = size  # Maximum number of elements in the buffer
        self.buffer = deque(maxlen=size)  # Use deque with a fixed maxlen
        self.sum = 0  # Maintain the sum of elements for efficient averaging

    def add(self, value):
        # If the buffer is full, subtract the value being removed from the sum
        if len(self.buffer) == self.size:
            self.sum -= self.buffer[0]

        # Add the new value to the buffer and update the sum
        self.buffer.append(value)
        self.sum += value

    def get_average(self):
        # Return the average of the elements in the buffer
        if len(self.buffer) == 0:
            return 0  # Avoid division by zero if the buffer is empty
        return self.sum / len(self.buffer)

    def get_buffer(self):
        # Return the current elements in the buffer
        return list(self.buffer)



# Define callback functions for the trackbars

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
    kernel_size = 5
    canny_threshold_min = 5
    canny_threshold_max = 15
    blur_kernel_size = 19  # Initial blur kernel size

    # ROI position. 
    ROI_scale = 70
    ROI_scale_bottom = 90

    # controls of contour
    min_area = 300    # Minimum contour length for filtering
    max_area = 10000  # Maximum contour length for filtering
    max_aspect_ratio= 3 #2
    max_circularity= 0.5 #0.5 
    max_extent= 0.5 #0.5

    # waiting time
    time=30

    #dimension of rolling buffer.
    rolling_buffer = RollingBuffer(size=3)


    x_v = []
    area_v = []

    while True:
        filename = f"{image_number}.jpg"  # Assuming images are named as numbers with .jpg extension
        file_path = os.path.join(images_folder, filename)

        # Check if the image file exists
        if os.path.isfile(file_path):
            # print(f"Displaying image: {filename}")
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
                kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 40))

                # Apply Canny edge detection
                edges = cv2.Canny(blurred_roi, canny_threshold_min, canny_threshold_max)

                # Perform morphological closing to connect edges
                closed_edges = cv2.dilate(edges, kernel1, iterations=1)
                closed_edges = cv2.morphologyEx(closed_edges, cv2.MORPH_CLOSE, kernel2)

                # Find contours of the closed edges
                contours_edge, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                #reset values
                x_v = []
                area_v=[]
                # Filter contours by length
                filtered_contours = []
                for contour in contours_edge:
                    area = cv2.contourArea(contour)
                    if min_area <= area <= max_area:
                        # Calculate the bounding rectangle
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = float(w) / h if h != 0 else 0  # Avoid division by zero

                        # Calculate additional features
                        rect_area = w * h  # Area of the bounding rectangle
                        extent = area / rect_area if rect_area != 0 else 0  # Ratio of contour area to bounding rectangle area
                        hull = cv2.convexHull(contour)  # Convex hull of the contour
                        hull_area = cv2.contourArea(hull)  # Area of the convex hull
                        solidity = area / hull_area if hull_area != 0 else 0  # Ratio of contour area to hull area
                        perimeter = cv2.arcLength(contour, True)
                        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter != 0 else 0  # Compactness of the shape

                        # Print features for debugging
                        print(f"Contour features:")
                        print(f" - Area: {area}")
                        print(f" - Aspect Ratio: {aspect_ratio}")
                        print(f" - Extent: {extent}")
                        print(f" - Solidity: {solidity}")
                        print(f" - Circularity: {circularity}")



                        # Filter criteria: keep long and narrow shapes
                        if aspect_ratio < max_aspect_ratio :  # Very narrow shapes
                            if circularity < max_circularity:
                                if extent < max_extent:
                                    filtered_contours.append(contour)
                                    area_v.append(area)

                                    # Compute centroid
                                    M = cv2.moments(contour)
                                    if M["m00"] != 0:
                                        cx = int(M["m10"] / M["m00"])
                                    else:
                                        cx = 0
                                    x_v.append(cx)

                # convert into numpy array
                area_v=np.array(area_v)
                x_v=np.array(x_v)
               
                # Calculate the weighted sum
                if np.sum(area_v) != 0:
                    weighted = np.sum(area_v * x_v) / np.sum(area_v)
                else:
                    weighted = 0  # Handle the case where the sum of area_v is zero

                # add to the rolling buffer
                if weighted != 0:
                    rolling_buffer.add( weighted )

                # Print the weighted value
                # print("Weighted Sum:", weighted)
                average = rolling_buffer.get_average()
                print("Average:", average)  # Output: 30.0






                # Create an RGB image from the red channel
                r_with_edges = cv2.merge([r_channel, r_channel, r_channel])
                roi_overlay = r_with_edges[ROI_scale * height // 100:ROI_scale_bottom * height // 100, :]

                # Draw filtered contours
                cv2.drawContours(roi_overlay, filtered_contours, -1, (0, 255, 0), thickness=2)

                # Draw ROI rectangle
                cv2.rectangle(r_with_edges, (0, ROI_scale * height // 100),
                              (width, ROI_scale_bottom * height // 100), (0, 0, 255), 2)

                # Calculate the center of the ROI
                roi_center_y = (ROI_scale + ROI_scale_bottom) * height // 200  # Average of the top and bottom ROI bounds
                weighted_x = int(average)  # Convert weighted sum to an integer pixel position

                # Draw a blue ball (circle) at the calculated position
                cv2.circle(r_with_edges, (weighted_x, roi_center_y), radius=5, color=(255, 0, 0), thickness=-1)


                # Create a window with trackbars
                cv2.namedWindow("Red Channel with Edges", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Red Channel with Edges", 800, 600)
                cv2.createTrackbar("Kernel Size", "Red Channel with Edges", kernel_size, 100, update_kernel_size)
                cv2.createTrackbar("Canny Thresh min", "Red Channel with Edges", canny_threshold_min, 255,
                                   update_canny_threshold_min)
                cv2.createTrackbar("Canny Thresh max", "Red Channel with Edges", canny_threshold_max, 255,
                                   update_canny_threshold_max)
                cv2.createTrackbar("Blur Kernel Size", "Red Channel with Edges", blur_kernel_size, 21, update_blur_kernel)

                # Display the image
                cv2.imshow("Red Channel with Edges", r_with_edges)
                
                key = cv2.waitKey(time)
                # key = cv2.waitKey()

                # If 'q' is pressed, exit the loop
                if key == ord('q'):
                    print("Exiting...")
                    break
                
                if key == ord('g'):
                    if time==30:
                        time=0
                    else:
                        time=30


            except Exception as e:
                print(f"Could not process image {filename}: {e}")

        else:
            print(f"Image {filename} not found. Ending loop.")
            break

        image_number += 1

    cv2.destroyAllWindows()
