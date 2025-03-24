from flask import Flask, request, render_template
import requests

app = Flask(__name__)
API_KEY = "YOUR_API_KEY"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather")
def weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecasts = []
        for i in range(0, len(data['list']), 8):  # every 8 entries = ~24 hours
            entry = data['list'][i]
            forecasts.append({
                'date': entry['dt_txt'],
                'temp': entry['main']['temp'],
                'description': entry['weather'][0]['description'],
                'wind': entry['wind']['speed']
            })
        city = data['city']['name']
        return {"city": city, "forecasts": forecasts}
    return {"error": "Could not retrieve weather data"}

if __name__ == "__main__":
    app.run(debug=True)
