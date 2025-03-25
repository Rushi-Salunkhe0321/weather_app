from flask import Flask, request, render_template, jsonify
import requests
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("api_key") 

# ✅ Add this route BEFORE the main "/" route
@app.route("/get_dates")
def get_dates():
    location = request.args.get("location")
    if not location:
        return jsonify({"error": "Location required"})

    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
    geo_response = requests.get(geo_url).json()

    if not geo_response:
        return jsonify({"error": "Location not found"})

    lat = geo_response[0]['lat']
    lon = geo_response[0]['lon']

    weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    response = requests.get(weather_url)
    if response.status_code != 200:
        return jsonify({"error": "Could not fetch forecast"})

    data = response.json()
    grouped_data = defaultdict(list)
    for entry in data['list']:
        date = entry['dt_txt'].split(' ')[0]
        grouped_data[date].append(entry)

    return jsonify({
        "dates": list(grouped_data.keys()),
        "city": data["city"]["name"]
    })

# ✅ Your main route stays as is
@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    error = None
    selected_date = None
    available_dates = []

    if request.method == "POST":
        location = request.form['location']
        selected_date = request.form.get('forecast_day')  # Optional

        # Step 1: Get coordinates
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
        geo_response = requests.get(geo_url).json()

        if not geo_response:
            error = "Location not found. Please enter a valid city or ZIP code."
        else:
            lat = geo_response[0]['lat']
            lon = geo_response[0]['lon']

            # Step 2: Get 5-day/3-hour forecast
            weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
            response = requests.get(weather_url)

            if response.status_code == 200:
                data = response.json()

                # Step 3: Group by date
                grouped_data = defaultdict(list)
                for entry in data['list']:
                    date = entry['dt_txt'].split(' ')[0]
                    grouped_data[date].append({
                        'time': entry['dt_txt'],
                        'temp': entry['main']['temp'],
                        'description': entry['weather'][0]['description'],
                        'wind': entry['wind']['speed'],
                        'icon': entry['weather'][0]['icon']
                    })

                available_dates = list(grouped_data.keys())

                # Show full 5-day summary or hourly forecast for selected day
                if selected_date and selected_date in grouped_data:
                    forecasts = grouped_data[selected_date]
                    view_type = "hourly"
                else:
                    # Daily summary: pick 1st entry per day
                    forecasts = [entries[0] for entries in grouped_data.values()]
                    view_type = "daily"

                weather_data = {
                    'city': data['city']['name'],
                    'forecasts': forecasts,
                    'view_type': view_type,
                    'selected_date': selected_date
                }
            else:
                error = "Failed to retrieve weather data."

    return render_template("index.html", weather=weather_data, error=error, available_dates=available_dates)


if __name__ == "__main__":
    app.run(debug=True)
