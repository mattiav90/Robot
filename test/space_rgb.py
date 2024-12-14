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

    threshold_min_value = 0  # Initial minimum threshold value
    threshold_max_value = 150  # Initial maximum threshold value

    # Create a separate window for the thresholded saturation
    cv2.namedWindow("Thresholded Saturation", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Thresholded Saturation", 800, 600)
    cv2.createTrackbar("Min Threshold", "Thresholded Saturation", threshold_min_value, 255, update_threshold_min)
    cv2.createTrackbar("Max Threshold", "Thresholded Saturation", threshold_max_value, 255, update_threshold_max)

    combined_display = 0
    thresholded_saturation = 0
    cv2.imshow("Combined HUE, Saturation, Value Channels", combined_display)
    cv2.imshow("Thresholded Saturation", thresholded_saturation)
    cv2.moveWindow("Combined HUE, Saturation, Value Channels", 0, 0)
    cv2.moveWindow("Thresholded Saturation", 600, 0)

    ROI_scale = 3

    while True:
        filename = f"{image_number}.jpg"  # Assuming images are named as numbers with .jpg extension
        file_path = os.path.join(images_folder, filename)

        # Check if the image file exists
        if os.path.isfile(file_path):
            print(f"Displaying image: {filename}")
            try:
                img = cv2.imread(file_path)

                #RGB channels
                b_channel, g_channel, r_channel = cv2.split(img)

                # Define ROI as the bottom third of the image
                height, width = r_channel.shape
                roi_cr = r_channel[2 * height // ROI_scale:, :]

                # Calculate the average gray value in the Cr channel ROI
                avg_cr_value = np.mean(roi_cr)
                print("Average gray value in Cr channel (ROI): ",avg_cr_value," ")

                # Apply threshold on the Cr channel
                thresholded_saturation = cv2.inRange(roi_cr, threshold_min_value, threshold_max_value)

                # Stack the channels together for display
                y_display = cv2.merge([r_channel, r_channel, r_channel])
                cr_display = cv2.merge([g_channel, g_channel, g_channel])
                cb_display = cv2.merge([b_channel, b_channel, b_channel])
                combined_display = np.vstack([y_display, cr_display, cb_display])

                # Resize for consistent display
                combined_display = cv2.resize(combined_display, (800, 600))

                # Display the combined image
                cv2.imshow("Combined Y, Cr, Cb Channels", combined_display)

                # Display the thresholded Cr channel in a separate window
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
