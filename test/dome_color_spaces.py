import os
import cv2
import numpy as np

# Define the root folder and the images folder
root_folder = "/home/mattiav90/Desktop/Robot"  # Replace with the actual path to the root folder
images_folder = os.path.join(root_folder, "imgs_saved/imgs1")  # Replace "images" with the name of your images folder

# Check if the images folder exists
if not os.path.exists(images_folder):
    print(f"The folder {images_folder} does not exist.")
else:
    # Start from image "1" and go up
    image_number = 1

    while True:
        filename = f"{image_number}.jpg"  # Assuming images are named as numbers with .jpg extension
        file_path = os.path.join(images_folder, filename)

        # Check if the image file exists
        if os.path.isfile(file_path):
            print(f"Processing image: {filename}")
            try:
                img = cv2.imread(file_path)

                # Convert the image to HSV
                hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                hue_channel = hsv_img[:, :, 0]
                saturation_channel = hsv_img[:, :, 1]
                value_channel = hsv_img[:, :, 2]

                cv2.imshow("s:",saturation_channel)

                # Convert the image to LAB
                lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
                l_channel = lab_img[:, :, 0]
                a_channel = lab_img[:, :, 1]
                b_channel = lab_img[:, :, 2]

                # Convert the image to YCrCb
                ycrcb_img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
                y_channel = ycrcb_img[:, :, 0]
                cr_channel = ycrcb_img[:, :, 1]
                cb_channel = ycrcb_img[:, :, 2]

                cv2.imshow("cr_channel: ",cr_channel)

                #RGB channels
                b_channel, g_channel, r_channel = cv2.split(img)

                # Stack and display independent channels for each color space
                hsv_display = np.hstack([hue_channel, saturation_channel, value_channel])
                lab_display = np.hstack([l_channel, a_channel, b_channel])
                ycrcb_display = np.hstack([y_channel, cr_channel, cb_channel])
                rgb_display = np.hstack([b_channel, g_channel, r_channel])

                # Resize for better visualization
                x=900
                y=210
                hsv_display = cv2.resize(hsv_display, (x, y))
                lab_display = cv2.resize(lab_display, (x, y))
                ycrcb_display = cv2.resize(ycrcb_display, (x, y))
                rgb_display = cv2.resize(rgb_display, (x, y))


                big_display = np.vstack([hsv_display, lab_display, ycrcb_display, rgb_display])
                # big_display = hsv_display
                cv2.imshow("Combined Channels Display", big_display)
                cv2.moveWindow("Combined Channels Display",0,0)



                # cv2.moveWindow("HSV Channels (H, S, V)",(0,0))
                # cv2.moveWindow("LAB Channels (L, A, B)",(0,200))
                # cv2.moveWindow("YCrCb Channels (Y, Cr, Cb)",(0,400))
                # cv2.moveWindow("RGB Channels (R, G, B)",(500,0))

                key = cv2.waitKey(200)

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
