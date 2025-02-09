import os
import re
import cv2

def get_sorted_images(folder_path):
    """
    Retrieves image filenames from the folder and sorts them numerically.
    """
    # List all files in the folder
    files = os.listdir(folder_path)
    
    # Filter only image files with numerical names and extensions
    images = [f for f in files if re.match(r"^\d+\.(jpg|jpeg|png|bmp|gif)$", f, re.IGNORECASE)]
    
    # Sort files numerically based on the numerical part of the filename
    images.sort(key=lambda x: int(re.search(r"(\d+)", x).group(1)))
    
    return images

def rename_images(folder_path):
    """
    Renames images sequentially starting from 1.jpg using OpenCV.
    """
    images = get_sorted_images(folder_path)
    
    if not images:
        print("No valid image files found in the folder.")
        return

    print(f"Found {len(images)} images. Renaming...")

    # Rename images sequentially
    for idx, old_name in enumerate(images, start=1):
        new_name = f"{idx+1184}.jpg"  # Rename all images to .jpg
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)

        # Read the image using OpenCV
        image = cv2.imread(old_path)
        if image is None:
            print(f"Error reading file: {old_name}. Skipping...")
            continue

        # Write (save) the image to the new filename
        cv2.imwrite(new_path, image)
        os.remove(old_path)  # Remove the old file
        print(f"Renamed: {old_name} -> {new_name}")
    
    print("Renaming completed successfully!")

if __name__ == "__main__":
    folder_path = os.getcwd()  # Use the current folder where the script is located
    rename_images(folder_path)

