import cv2
import os
import argparse
import numpy as np

def is_blurry(image_path, threshold=100.0):
    """
    Determines if an image is blurry based on the variance of the Laplacian.

    Args:
        image_path (str): The path to the image file.
        threshold (float): The variance threshold below which the image is considered blurry.

    Returns:
        bool: True if the image is blurry, False otherwise.
        float: The calculated variance of the Laplacian.
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold, laplacian_var

def rate_blur_in_folder(folder_path, threshold=100.0):
    """
    Rates images in a folder based on their blurriness.

    Args:
        folder_path (str): The path to the folder containing PNG images.
        threshold (float): The variance threshold below which images are considered blurry.

    Returns:
        None: Prints the blurriness rating for each image.
    """
    if not os.path.exists(folder_path):
        print("Error: The specified folder path does not exist.")
        return

    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    
    if not png_files:
        print("No PNG files found in the specified folder.")
        return

    for image_file in png_files:
        image_path = os.path.join(folder_path, image_file)
        blurry, laplacian_var = is_blurry(image_path, threshold)
        status = "Blurry" if blurry else "Not Blurry"
        print(f"{image_file}: {status} (Laplacian Variance: {laplacian_var:.2f})")

def main():
    parser = argparse.ArgumentParser(description="Rate images in a folder for blurriness.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing PNG images.")
    parser.add_argument("--threshold", type=float, default=100.0, help="Blurriness threshold (default: 100.0). Lower values mean blurrier.")
    args = parser.parse_args()

    rate_blur_in_folder(args.folder_path, args.threshold)

if __name__ == "__main__":
    main()
