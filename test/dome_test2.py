import os
import cv2
import numpy as np

# Define the root folder and the images folder
root_folder = "/home/mattiav90/Desktop/Robot"  # Replace with the actual path to the root folder
images_folder = os.path.join(root_folder, "imgs_saved/dome/1")  # Replace "images" with the name of your images folder

# Define callback functions for the trackbars
def update_threshold_min(val):
    global threshold_min_value
    threshold_min_value = val

def update_threshold_max(val):
    global threshold_max_value
    threshold_max_value = val

# Check if the images folder exists
if not os.path.exists(images_folder):
    print(f"The folder {images_folder} does not exist.")
else:
    # Start from image "1" and go up
    image_number = 1

    threshold_min_value = 50  # Initial minimum threshold value
    threshold_max_value = 230  # Initial maximum threshold value

    # Create a separate window for the thresholded saturation
    cv2.namedWindow("Thresholded Saturation", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Thresholded Saturation", 800, 600)
    cv2.createTrackbar("Min Threshold", "Thresholded Saturation", threshold_min_value, 255, update_threshold_min)
    cv2.createTrackbar("Max Threshold", "Thresholded Saturation", threshold_max_value, 255, update_threshold_max)

    combined_display=0
    thresholded_saturation=0
    cv2.imshow("Combined HUE, Saturation, Value Channels", combined_display)
    cv2.imshow("Thresholded Saturation", thresholded_saturation)
    cv2.moveWindow("Combined HUE, Saturation, Value Channels",0,0)
    cv2.moveWindow("Thresholded Saturation",800,0)

    while True:
        filename = f"{image_number}.jpg"  # Assuming images are named as numbers with .jpg extension
        file_path = os.path.join(images_folder, filename)

        # Check if the image file exists
        if os.path.isfile(file_path):
            print(f"Displaying image: {filename}")
            try:
                img = cv2.imread(file_path)

                # Convert the image to HSV
                hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

                # Extract the HUE, Saturation, and Value channels
                hue_channel = hsv_img[:, :, 0]
                saturation_channel = hsv_img[:, :, 1]
                value_channel = hsv_img[:, :, 2]

                # Define ROI as the bottom half of the image
                height, width = hue_channel.shape
                roi_hue = hue_channel[height // 3:, :]
                roi_saturation = saturation_channel[height // 3:, :]
                roi_value = value_channel[height // 3:, :]

                # Apply threshold on the saturation channel
                thresholded_saturation = cv2.inRange(roi_saturation, threshold_min_value, threshold_max_value)

                # Stack the channels together for display
                hue_display = cv2.merge([roi_hue, roi_hue, roi_hue])
                saturation_display = cv2.merge([roi_saturation, roi_saturation, roi_saturation])
                value_display = cv2.merge([roi_value, roi_value, roi_value])
                combined_display = np.vstack([hue_display, saturation_display, value_display])

                # Resize for consistent display
                combined_display = cv2.resize(combined_display, (800, 600))

                # Display the combined image
                cv2.imshow("Combined HUE, Saturation, Value Channels", combined_display)

                # Display the thresholded saturation in a separate window
                cv2.imshow("Thresholded Saturation", thresholded_saturation)

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
