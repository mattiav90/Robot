import os
import cv2
import numpy as np
from collections import deque

# Define the root folder and the images folder
root_folder = "/home/mattiav90/Desktop/Robot"  # Replace with the actual path to the root folder
images_folder = os.path.join(root_folder, "imgs_saved/dome/1")  # Replace "images" with the name of your images folder


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
    kernel_size = 11
    canny_threshold_min = 5
    canny_threshold_max = 15
    blur_kernel_size = 19  # Initial blur kernel size

    # ROI position. 
    ROI_scale = 70
    ROI_scale_bottom = 90
    ROI_scale_line = ROI_scale+(ROI_scale_bottom-ROI_scale)/2

    # number of printed lines:
    line_number=10

    # waiting time
    time=30

    #dimension of rolling buffer.
    rolling_buffer = RollingBuffer(size=7)


    x_v = []
    area_v = []

while True:
    filename = f"{image_number}.jpg"  # Assuming images are named as numbers with .jpg extension
    file_path = os.path.join(images_folder, filename)

    # Check if the image file exists
    if os.path.isfile(file_path):
        try:
            img = cv2.imread(file_path)

            # Extract the red channel
            _, _, r_channel = cv2.split(img)

            # Define ROI
            height, width = r_channel.shape
            roi = r_channel[ROI_scale * height // 100:ROI_scale_bottom * height // 100, :]

            masko=np.zeros(img.shape,dtype=np.uint8())
            mask=np.zeros(img.shape,dtype=np.uint8())

            # Apply Gaussian Blur to reduce noise
            blurred_roi = cv2.GaussianBlur(roi, (blur_kernel_size, blur_kernel_size), 0)

            # Update kernels dynamically based on the trackbar
            kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size*2))
            kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 40))

            # Apply Canny edge detection
            edges = cv2.Canny(blurred_roi, canny_threshold_min, canny_threshold_max)

            # Perform morphological closing to connect edges
            closed_edges = cv2.dilate(edges, kernel1, iterations=1)
            closed_edges = cv2.morphologyEx(closed_edges, cv2.MORPH_CLOSE, kernel2)

            # Fit a line in the ROI using Hough Line Transform
            lines = cv2.HoughLines(closed_edges, rho=1, theta=np.pi / 180, threshold=150)

            # generate image. 
            r_with_edges = cv2.merge([r_channel, r_channel, r_channel])

            if lines is not None:                
                # Calculate line lengths and store them along with coordinates
                line_details = []
                for rho, theta in lines[:line_number, 0]:
                    # Convert polar coordinates (rho, theta) to Cartesian points
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * a)
                    x2 = int(x0 - 1000 * (-b))
                    y2 = int(y0 - 1000 * a)

                    y_offset = ROI_scale * height // 100  # Adjust for ROI position
                    cv2.line(mask, (x1, y1 + y_offset), (x2, y2 + y_offset), (255,255,255), 2)

            else:
                print("No lines detected in the ROI.")

            # Draw a line in the middle of the ROI
            cv2.line(masko, (0, int(ROI_scale_line * height // 100)), (width, int(ROI_scale_line * height // 100)), (255,255,255), 2)

            intersection = cv2.bitwise_and(mask, masko)
            _, binary_intersection = cv2.threshold(intersection, 127, 255, cv2.THRESH_BINARY)

            # cv2.imshow("int",intersection)

            # Ensure binary_intersection is binary and single-channel
            if len(binary_intersection.shape) > 2:
                binary_intersection = cv2.cvtColor(binary_intersection, cv2.COLOR_BGR2GRAY)

            kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            binary_intersection = cv2.dilate(binary_intersection, kernel1, iterations=1)
            binary_intersection = cv2.morphologyEx(binary_intersection, cv2.MORPH_CLOSE, kernel1)
            

            # Ensure 'intersection' is binary
            contours, hierarchy = cv2.findContours(binary_intersection, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # cv2.imshow("po",binary_intersection)

            # Optional: Draw contours for visualization
            output_image = cv2.cvtColor(binary_intersection, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(r_with_edges, contours, -1, (0, 255, 0), 2)

            

            # Draw ROI rectangle
            cv2.rectangle(r_with_edges, (0, ROI_scale * height // 100),
                          (width, ROI_scale_bottom * height // 100), (0, 0, 255), 2)


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

            # If 'q' is pressed, exit the loop
            if key == ord('q'):
                print("Exiting...")
                break
            
            if key == ord('g'):
                time = 0 if time == 30 else 30

        except Exception as e:
            print(f"Could not process image {filename}: {e}")

    else:
        print(f"Image {filename} not found. Ending loop.")
        break

    image_number += 1

cv2.destroyAllWindows()
