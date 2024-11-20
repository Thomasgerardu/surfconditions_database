import cv2
import os
from typing import Tuple


def is_blurry(image_path: str, threshold: float) -> Tuple[bool, float]:
    """
    Determines if an image is blurry based on the variance of the Laplacian.

    Args:
        image_path (str): The path to the image file.
        threshold (float): The variance threshold below which the image is considered blurry.

    Returns:
        Tuple[bool, float]: A tuple containing:
            - True if the image is blurry, False otherwise.
            - The calculated variance of the Laplacian.
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    return laplacian_var < threshold, laplacian_var


def cleanup_blurry_images(folder_path: str, threshold: float) -> None:
    """
    Deletes blurry images in a folder based on a given threshold.

    Args:
        folder_path (str): The path to the folder containing PNG images.
        threshold (float): The variance threshold below which images are considered blurry.

    Returns:
        None
    """
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        return

    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]

    if not png_files:
        print(f"No PNG files found in {folder_path}.")
        return

    for image_file in png_files:
        image_path = os.path.join(folder_path, image_file)
        blurry, laplacian_var = is_blurry(image_path, threshold)
        if blurry:
            os.remove(image_path)  # Permanently delete the file
            print(f"Deleted: {image_file} (Laplacian Variance: {laplacian_var:.2f})")


def main() -> None:
    """
    Main function to clean up blurry images in the specified folders.
    """
    # Cleanup for data_aloha folder
    cleanup_blurry_images(
        folder_path="data_aloha",
        threshold=139.0  # Threshold for aloha
    )

    # Cleanup for data_heartbeach folder
    cleanup_blurry_images(
        folder_path="data_heartbeach",
        threshold=51.0  # Threshold for heartbeach
    )


if __name__ == "__main__":
    main()
