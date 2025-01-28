import cv2
import os
import matplotlib.pyplot as plt


def plot_rgb(img,y_pos,id):
    
    b,g,r = cv2.split(img)
    x_dim,y_dim,ch= img.shape
    scale = 2.7
    y_dim_plot = int(x_dim/scale)
    x_dim_plot = int(y_dim/scale)
    cv2.namedWindow(f"img {id}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"img {id}", x_dim_plot, y_dim_plot)
    cv2.moveWindow(f"img {id}", x_dim_plot*0, y_pos)
    cv2.imshow(f"img {id}", img)
    # red img
    cv2.namedWindow(f"R {id}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"R {id}", x_dim_plot, y_dim_plot)
    cv2.moveWindow(f"R {id}", x_dim_plot*1, y_pos)
    cv2.imshow(f"R {id}", r)
    # green img
    cv2.namedWindow(f"G {id}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"G {id}", x_dim_plot, y_dim_plot)
    cv2.moveWindow(f"G {id}", x_dim_plot*2, y_pos)
    cv2.imshow(f"G {id}", g)
    # blu img
    cv2.namedWindow(f"B {id}", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"B {id}", x_dim_plot, y_dim_plot)
    cv2.moveWindow(f"B {id}", x_dim_plot*3, y_pos)
    cv2.imshow(f"B {id}", b)



def load_single_img(path):
    """
    Load a single image from the given path.

    Args:
        path (str): Path to the image.

    Returns:
        img: Loaded image or None if the path doesn't exist or the image cannot be loaded.
    """
    if not os.path.exists(path):
        print("The path:", path, "does not exist.")
        return None

    img = cv2.imread(path)
    if img is None:
        print("Unable to load the image from:", path)
    return img


def load_img(path, display_time, calib_img):
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

        # Subtract the calibration image from the current image
        sub = cv2.subtract(img, calib_img)
        
        x_dim,y_dim,ch= sub.shape





        # ******** plot ********
        plot_rgb(sub,0,0)
        plot_rgb(img,int(y_dim/3),1)




        # Wait for the specified time or until 'q' is pressed
        if cv2.waitKey(int(display_time * 1000)) & 0xFF == ord('q'):
            print("Exiting...")
            break

    # Destroy all OpenCV windows after exiting the loop
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Path to the calibration image
    calib_path = "./imgs_saved/imgs1/calib.jpg"
    calib = load_single_img(calib_path)
    filter_size=11
    blurred_calib = cv2.GaussianBlur(calib,(filter_size,filter_size),0)

    if calib is not None:

        # Path to the directory containing images
        path = "./imgs_saved/imgs1/"
        load_img(path, 0.1, calib)
    else:
        print("Calibration image could not be loaded.")
