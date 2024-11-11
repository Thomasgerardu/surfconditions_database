from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Directory where screenshots are stored
DATA_DIR = "data"

def find_best_matches(wave_height=None, wave_period=None, wave_direction=None, wind_speed=None, wind_direction=None, top_n=5):
    matches = []

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".png"):
            try:
                parts = filename.split("_")
                file_wave_height = float(parts[1][:-1])  # "0.5m" -> 0.5
                file_wave_period = float(parts[2][:-1])   # "5s" -> 5
                file_wave_direction = parts[0]           # "NNE", etc.
                file_wind_speed = float(parts[4][:-3])    # "3.2kmh" -> 3.2
                file_wind_direction = parts[3]           # "SE", etc.

                # Calculate score based on available inputs
                score = 0
                if wave_height is not None:
                    score += abs(file_wave_height - wave_height) * 10  # Weight for wave height
                if wave_period is not None:
                    score += abs(file_wave_period - wave_period)
                if wave_direction:
                    score += 0 if file_wave_direction == wave_direction else 5  # Penalize mismatched direction
                if wind_speed is not None:
                    score += abs(file_wind_speed - wind_speed)
                if wind_direction:
                    score += 0 if file_wind_direction == wind_direction else 5

                matches.append((score, filename))
            except (IndexError, ValueError):
                continue

    # Sort matches by score and return the top results
    matches.sort()
    return [match[1] for match in matches[:top_n]]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
# @app.route('/search', methods=['POST'])
def search():
    # Retrieve each parameter if present, otherwise set to None
    wave_height = float(request.form.get('wave_height')) if request.form.get('wave_height') else None
    wave_period = float(request.form.get('wave_period')) if request.form.get('wave_period') else None
    wave_direction = request.form.get('wave_direction') if request.form.get('wave_direction') else None
    wind_speed = float(request.form.get('wind_speed')) if request.form.get('wind_speed') else None
    wind_direction = request.form.get('wind_direction') if request.form.get('wind_direction') else None

    # Call find_best_matches with the specified parameters
    matches = find_best_matches(
        wave_height=wave_height,
        wave_period=wave_period,
        wave_direction=wave_direction,
        wind_speed=wind_speed,
        wind_direction=wind_direction
    )

    # Return the list of matching filenames as JSON
    return jsonify(matches)


if __name__ == '__main__':
    app.run(debug=True)
