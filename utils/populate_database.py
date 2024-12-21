import os
import sqlite3

# Paths to the data folders
DATA_FOLDERS = {
    # "data_aloha": "data_aloha",
    # "data_heartbeach": "data_heartbeach"
    "data": "test_pics"
}

# Database path
DATABASE_PATH = "surfconditions.db"

# Function to parse metadata from filenames
def parse_filename(filename):
    """
    Parses a filename to extract metadata.

    Expected format:
    waveDirection_waveHeightm_wavePeriods_windDirection_windSpeedkmh_tideregime_timestamp.png

    Example:
    N_0.5m_5s_SE_3.2kmh_lm_20231101_120000.png

    Returns:
        A dictionary with parsed values or None if the filename is invalid.
    """
    try:
        parts = filename.split("_")
        wave_direction = parts[0]
        wave_height = float(parts[1][:-1])  # "0.5m" -> 0.5
        wave_period = float(parts[2][:-1])  # "5s" -> 5
        wind_direction = parts[3]
        wind_speed = float(parts[4][:-3])  # "3.2kmh" -> 3.2

        return {
            "wave_direction": wave_direction,
            "wave_height": wave_height,
            "wave_period": wave_period,
            "wind_direction": wind_direction,
            "wind_speed": wind_speed
        }
    except (IndexError, ValueError):
        print(f"Filename {filename} is invalid. Skipping.")
        return None

# Function to populate the database
def populate_database():
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    # Clear the existing data in the images table
    cur.execute("DELETE FROM images;")  # Removes all rows from the table
    conn.commit()  # Apply the deletion

    # Iterate through each folder and file
    for folder_label, folder_path in DATA_FOLDERS.items():
        if not os.path.exists(folder_path):
            print(f"Folder {folder_path} does not exist. Skipping.")
            continue

        for filename in os.listdir(folder_path):
            if not filename.endswith((".png", ".jpg")):
                continue

            # Parse metadata from the filename
            metadata = parse_filename(filename)
            if metadata is None:
                continue

            # Insert metadata into the database
            try:
                cur.execute(
                    """
                    INSERT INTO images (filename, folder, wave_height, wave_period, wave_direction, wind_speed, wind_direction)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        filename,
                        folder_label,
                        metadata["wave_height"],
                        metadata["wave_period"],
                        metadata["wave_direction"],
                        metadata["wind_speed"],
                        metadata["wind_direction"]
                    )
                )
            except sqlite3.IntegrityError as e:
                print(f"Error inserting {filename}: {e}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Database population complete.")

if __name__ == "__main__":
    populate_database()
