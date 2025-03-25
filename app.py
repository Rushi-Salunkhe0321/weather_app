from flask import Flask, request, render_template
import requests

app = Flask(__name__)
API_KEY = "YOUR_API_KEY"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather", methods=["POST"])
def weather():
    location = request.form['location']

    # Step 1: Geocode the location
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
    geo_response = requests.get(geo_url)
    
    if geo_response.status_code != 200 or not geo_response.json():
        return {"error": "Location not found"}

    geo_data = geo_response.json()[0]
    lat, lon = geo_data['lat'], geo_data['lon']

    # Step 2: Get 5-day forecast
    weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    weather_response = requests.get(weather_url)

    if weather_response.status_code == 200:
        data = weather_response.json()
        forecasts = []
        for i in range(0, len(data['list']), 8):
            entry = data['list'][i]
            forecasts.append({
                'date': entry['dt_txt'],
                'temp': entry['main']['temp'],
                'description': entry['weather'][0]['description'],
                'wind': entry['wind']['speed']
            })
        city = data['city']['name']
        return render_template("index.html", city=city, forecasts=forecasts)
    else:
        return {"error": "Could not retrieve weather data"}

if __name__ == "__main__":
    app.run(debug=True)
