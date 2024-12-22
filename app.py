from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import sqlite3

app = Flask(__name__)

# Define the data directories
# DATA_DIRS = {
#     "data_aloha": "data_aloha",
#     "data_heartbeach": "data_heartbeach"
# }
DATA_DIRS = {
    "data": "test_pics"
}
# Path to the SQLite database
DATABASE_PATH = "surfconditions.db"
# DATABASE_PATH = "surfdatabase_test.db"
# Map to 8 primary compass directions
PRIMARY_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

def simplify_direction(direction):
    """
    Simplifies 16-point compass directions to 8-point compass directions.
    """
    mapping = {
        "N": "N", "NNE": "N", "NE": "NE", "ENE": "NE",
        "E": "E", "ESE": "E", "SE": "SE", "SSE": "SE",
        "S": "S", "SSW": "S", "SW": "SW", "WSW": "SW",
        "W": "W", "WNW": "W", "NW": "NW", "NNW": "NW"
    }
    return mapping.get(direction, direction)

def calculate_score(file_metadata, user_input):
    """
    Calculates a weighted score based on the user's input and file metadata.

    Args:
        file_metadata (dict): Metadata for the file (wave_height, wave_period, etc.).
        user_input (dict): User-provided surf conditions.

    Returns:
        float: The calculated score.
    """
    wave_height = user_input.get("wave_height")
    wave_period = user_input.get("wave_period")
    wave_direction = user_input.get("wave_direction")
    wind_speed = user_input.get("wind_speed")
    wind_direction = user_input.get("wind_direction")

    # Initialize score
    score = 0

    # Wave height (50%)
    if wave_height is not None:
        score += (abs(file_metadata["wave_height"] - wave_height) / 3) * 50

    # Wind speed (20%)
    if wind_speed is not None:
        score += (abs(file_metadata["wind_speed"] - wind_speed) / 60) * 20

    # Wave direction (15%)
    if wave_direction:
        file_wave_direction = simplify_direction(file_metadata["wave_direction"])
        if file_wave_direction != wave_direction:
            score += 15

    # Wind direction (15%)
    if wind_direction:
        file_wind_direction = simplify_direction(file_metadata["wind_direction"])
        if file_wind_direction != wind_direction:
            score += 15

    # Wave period (optional, lesser weight)
    if wave_period is not None:
        score += abs(file_metadata["wave_period"] - wave_period)

    return score


def find_best_matches(wave_height=None, wave_period=None, wave_direction=None, wind_speed=None, wind_direction=None, top_n=10):
    """
    Finds the best matching images based on the provided conditions.
    """
    # with sqlite3.connect("surfdatabase_test.db") as conn: #aanpassen
    with sqlite3.connect("surfdatabase.db") as conn: #aanpassen
        cur = conn.cursor()
        cur.execute("SELECT folder, filename, wave_height, wave_period, wave_direction, wind_speed, wind_direction FROM images_test") #aanpassen
        results = cur.fetchall()

    matches = []
    for row in results:
        folder, filename, file_wave_height, file_wave_period, file_wave_direction, file_wind_speed, file_wind_direction = row

        # Metadata for the file
        file_metadata = {
            "wave_height": file_wave_height,
            "wave_period": file_wave_period,
            "wave_direction": file_wave_direction,
            "wind_speed": file_wind_speed,
            "wind_direction": file_wind_direction
        }

        # User-provided input
        user_input = {
            "wave_height": wave_height,
            "wave_period": wave_period,
            "wave_direction": wave_direction,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction
        }

        # Calculate the score
        score = calculate_score(file_metadata, user_input)

        # Add the match with its score
        matches.append((score, folder, filename))

    # Sort matches by score (lowest score = better match)
    matches.sort(key=lambda x: x[0])

    # Return the top matches as URLs
    return [f"/serve/{match[1]}/{match[2]}" for match in matches[:top_n]]


@app.route('/serve/<folder>/<filename>')
def serve_image(folder, filename):
    """
    Dynamically serves images from the data folders.
    """
    if folder not in DATA_DIRS:
        return "Folder not found", 404
    folder_path = DATA_DIRS[folder]
    return send_from_directory(folder_path, filename)


@app.route('/')
def index():
    """
    Renders the main search page.
    """
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template("about.html")  # Your about page template


@app.route('/search', methods=['POST'])
def search():
    """
    Handles search requests and returns the top matching images with detailed metadata.
    """
    # Parse form data
    wave_height = float(request.form.get('wave_height')) if request.form.get('wave_height') else None
    wave_period = float(request.form.get('wave_period')) if request.form.get('wave_period') else None
    wave_direction = request.form.get('wave_direction') if request.form.get('wave_direction') else None
    wind_speed = float(request.form.get('wind_speed')) if request.form.get('wind_speed') else None
    wind_direction = request.form.get('wind_direction') if request.form.get('wind_direction') else None

    # Query the database and count total images
    with sqlite3.connect("surfconditions.db") as conn:
    # with sqlite3.connect("surfdatabase_test.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM images")
        # cur.execute("SELECT COUNT(*) FROM images_test")
        total_images = cur.fetchone()[0]

        cur.execute("SELECT folder, filename, wave_height, wave_period, wave_direction, wind_speed, wind_direction FROM images")
        # cur.execute("SELECT folder, filename, wave_height, wave_period, wave_direction, wind_speed, wind_direction FROM images_test")
        results = cur.fetchall()

    matches = []
    for row in results:
        folder, filename, file_wave_height, file_wave_period, file_wave_direction, file_wind_speed, file_wind_direction = row

        # Metadata for the file
        file_metadata = {
            "wave_height": file_wave_height,
            "wave_period": file_wave_period,
            "wave_direction": file_wave_direction,
            "wind_speed": file_wind_speed,
            "wind_direction": file_wind_direction
        }

        # User input
        user_input = {
            "wave_height": wave_height,
            "wave_period": wave_period,
            "wave_direction": wave_direction,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction
        }

        # Calculate score and differences
        score = calculate_score(file_metadata, user_input)
        differences = {
            "wave_height_diff": abs(file_wave_height - wave_height) if wave_height is not None else None,
            "wave_period_diff": abs(file_wave_period - wave_period) if wave_period is not None else None,
            "wave_direction_diff": file_wave_direction != wave_direction if wave_direction else None,
            "wind_speed_diff": abs(file_wind_speed - wind_speed) if wind_speed is not None else None,
            "wind_direction_diff": file_wind_direction != wind_direction if wind_direction else None,
        }

        matches.append({
            "score": score,
            "folder": folder,
            "filename": filename,
            "differences": differences
        })

    # Sort matches by score and return the top N
    matches.sort(key=lambda x: x["score"])

    # Add total_images to the response
    response = {
        "total_images": total_images,
        "matches": matches[:30]
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
