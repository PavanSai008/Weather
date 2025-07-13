from flask import Flask, jsonify, render_template, request
import requests
import numpy as np
import pickle
import os

app = Flask(__name__)

# WeatherAPI config
API_KEY = '37afff6c9bd34d41888100230251307'
BASE_URL = 'https://api.weatherapi.com/v1'
MAIN_CITY = 'Hyderabad'
POPULAR_CITIES = ['Delhi', 'Mumbai', 'Hyderabad', 'Bangalore', 'Kolkata']

# Rain prediction model config
MODEL_PATH = 'model.pkl'
SCALER_PATH = 'scaler.pkl'
FEATURE_COLUMNS_PATH = 'feature_columns.pkl'

if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH) and os.path.exists(FEATURE_COLUMNS_PATH):
    with open(MODEL_PATH, 'rb') as model_file:
        model = pickle.load(model_file)
    with open(SCALER_PATH, 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)
    with open(FEATURE_COLUMNS_PATH, 'rb') as f:
        feature_columns = pickle.load(f)
else:
    model = None
    scaler = None
    feature_columns = None

def fetch_weather_data(city):
    url = f"{BASE_URL}/current.json?key={API_KEY}&q={city}"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200 or "current" not in data:
            return {"error": data.get("error", {}).get("message", "City not found")}
        current = data["current"]
        # Map WeatherAPI fields to your model's expected features
        weather_features = {
            "pressure": current.get("pressure_mb", 0),
            "temperature": current.get("temp_c", 0),
            "dewpoint": current.get("dewpoint_c", 0) if "dewpoint_c" in current else current.get("temp_c", 0),
            "humidity": current.get("humidity", 0),
            "cloud": current.get("cloud", 0),
            "sunshine": 100 - current.get("cloud", 0),
            "winddirection": current.get("wind_degree", 0),
            "windspeed": current.get("wind_kph", 0)
        }
        return weather_features
    except Exception as e:
        return {"error": str(e)}

def get_rain_prediction(city):
    if not model or not scaler or not feature_columns:
        return None, None, "Model, scaler, or feature columns not loaded"
    weather_data = fetch_weather_data(city)
    if "error" in weather_data:
        return None, None, weather_data["error"]
    print("Weather data:", weather_data)
    print("Feature columns:", feature_columns)
    features = np.array([weather_data[col] for col in feature_columns]).reshape(1, -1)
    print("Features for model:", features)
    features_scaled = scaler.transform(features)
    print("Scaled features:", features_scaled)
    prediction = model.predict(features_scaled)[0]
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(features_scaled)[0][1]
        print("Predicted probability:", prob)
        percent = int(prob * 100)
    else:
        percent = None
    return ('Rain' if prediction == 1 else 'No Rain'), percent, None

@app.route('/')
def index():
    city = request.args.get('city', MAIN_CITY)
    print(f"Rendering index for city: {city}")
    prediction, percent, error = get_rain_prediction(city)
    return render_template('index.html', prediction=prediction, percent=percent, city=city, error=error)

@app.route('/api/current')
def get_current_weather():
    city = request.args.get('city', MAIN_CITY)
    url = f'{BASE_URL}/current.json?key={API_KEY}&q={city}'
    res = requests.get(url).json()
    return jsonify(res)

@app.route('/api/forecast')
def get_forecast():
    city = request.args.get('city', MAIN_CITY)
    url = f'{BASE_URL}/forecast.json?key={API_KEY}&q={city}&days=7'
    res = requests.get(url).json()
    return jsonify(res['forecast']['forecastday'])

@app.route('/api/popular')
def get_popular_cities_weather():
    data = {}
    for city in POPULAR_CITIES:
        url = f'{BASE_URL}/current.json?key={API_KEY}&q={city}'
        res = requests.get(url).json()
        data[city] = {
            'temp_c': res['current']['temp_c'],
            'condition': res['current']['condition']['text'],
            'icon': res['current']['condition']['icon']
        }
    return jsonify(data)

@app.route('/api/hourly')
def get_hourly():
    city = request.args.get('city', MAIN_CITY)
    url = f'{BASE_URL}/forecast.json?key={API_KEY}&q={city}&days=1'
    res = requests.get(url).json()
    return jsonify(res['forecast']['forecastday'][0]['hour'])

if __name__ == '__main__':
    app.run(debug=True)
