import cv2
import os
import argparse
import numpy as np
import csv

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
    laplacian_var = int(cv2.Laplacian(gray, cv2.CV_64F).var())
    return laplacian_var < threshold, laplacian_var

def rate_blur_in_folder(folder_path, threshold=100.0, output_csv="bluriness_ratings.csv"):
    """
    Rates images in a folder based on their blurriness and outputs a CSV file sorted by Laplacian variance.

    Args:
        folder_path (str): The path to the folder containing PNG images.
        threshold (float): The variance threshold below which images are considered blurry.
        output_csv (str): The name of the output CSV file to save the results.
    
    Returns:
        None: Writes the results to a CSV file.
    """
    if not os.path.exists(folder_path):
        return

    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    
    if not png_files:
        return

    bluriness_data = []

    for image_file in png_files:
        image_path = os.path.join(folder_path, image_file)
        blurry, laplacian_var = is_blurry(image_path, threshold)
        bluriness_data.append((image_file, laplacian_var))

    # Sort the data by Laplacian variance in descending order
    bluriness_data.sort(key=lambda x: x[1], reverse=True)

    # Write the results to a CSV file
    with open(output_csv, mode='w', newline='') as csvfile:
        fieldnames = ['Filename', 'Laplacian Variance']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter=";")

        writer.writeheader()
        for image_file, laplacian_var in bluriness_data:
            writer.writerow({'Filename': image_file, 'Laplacian Variance': laplacian_var})

def main():
    parser = argparse.ArgumentParser(description="Rate images in a folder for blurriness.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing PNG images.")
    parser.add_argument("--threshold", type=float, default=100.0, help="Blurriness threshold (default: 100.0). Lower values mean blurrier.")
    parser.add_argument("--output_csv", type=str, default="bluriness_ratings.csv", help="Output CSV file name (default: 'bluriness_ratings.csv').")
    args = parser.parse_args()

    rate_blur_in_folder(args.folder_path, args.threshold, args.output_csv)

if __name__ == "__main__":
    main()
