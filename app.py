from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import sqlite3

app = Flask(__name__)

# Define the data directories
DATA_DIRS = {
    "data_aloha": "data_aloha",
    "data_heartbeach": "data_heartbeach"
}

# Path to the SQLite database
DATABASE_PATH = "surfconditions.db"

# Function to find the best matches
def find_best_matches(wave_height=None, wave_period=None, wave_direction=None, wind_speed=None, wind_direction=None, top_n=10):
    query = "SELECT folder, filename FROM images WHERE 1=1"
    params = []

    if wave_height is not None:
        query += " AND wave_height BETWEEN ? AND ?"
        params.extend([wave_height - 0.5, wave_height + 0.5])  # Example range
    if wave_period is not None:
        query += " AND wave_period BETWEEN ? AND ?"
        params.extend([wave_period - 1, wave_period + 1])
    if wave_direction is not None:
        query += " AND wave_direction = ?"
        params.append(wave_direction)
    if wind_speed is not None:
        query += " AND wind_speed BETWEEN ? AND ?"
        params.extend([wind_speed - 2, wind_speed + 2])  # Example range
    if wind_direction is not None:
        query += " AND wind_direction = ?"
        params.append(wind_direction)

    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(top_n)

    with sqlite3.connect(DATABASE_PATH) as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        results = cur.fetchall()

    # Construct file paths for the results
    return [f"/serve/{folder}/{filename}" for folder, filename in results]


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


@app.route('/search', methods=['POST'])
def search():
    """
    Handles search requests and returns the top matching images.
    """
    # Parse form data
    wave_height = float(request.form.get('wave_height')) if request.form.get('wave_height') else None
    wave_period = float(request.form.get('wave_period')) if request.form.get('wave_period') else None
    wave_direction = request.form.get('wave_direction') if request.form.get('wave_direction') else None
    wind_speed = float(request.form.get('wind_speed')) if request.form.get('wind_speed') else None
    wind_direction = request.form.get('wind_direction') if request.form.get('wind_direction') else None

    # Find matches
    matches = find_best_matches(
        wave_height=wave_height,
        wave_period=wave_period,
        wave_direction=wave_direction,
        wind_speed=wind_speed,
        wind_direction=wind_direction
    )

    return jsonify(matches)


if __name__ == '__main__':
    app.run(debug=True)
