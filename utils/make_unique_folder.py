import os
import shutil

def copy_unique_images(source_folder, destination_folder):
    """
    Copies unique images from source_folder to destination_folder,
    ignoring the time part in their filenames.

    Args:
        source_folder (str): Path to the source folder containing images.
        destination_folder (str): Path to the destination folder for unique images.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    unique_files = set()

    for filename in os.listdir(source_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):  # Filter image files
            # Split filename by underscores
            parts = filename.split('_')

            if len(parts) > 2:  # Ensure filename follows expected format
                # Recreate the filename without the time part [-2]
                time_removed = '_'.join(parts[:7] + parts[8:])

                if time_removed not in unique_files:
                    unique_files.add(time_removed)
                    # Copy the unique file to the destination folder
                    shutil.copy(os.path.join(source_folder, filename),
                                os.path.join(destination_folder, filename))

if __name__ == "__main__":
    source_folder = r"C:\Github\surfconditions_database\data_aloha"
    destination_folder = os.path.join(r"C:\Github\surfconditions_database", "new_folder_unique")

    copy_unique_images(source_folder, destination_folder)

    print(f"Unique images have been copied to: {destination_folder}")
