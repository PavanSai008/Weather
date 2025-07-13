from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle
import os
import requests
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Load model and scaler
model_path = 'model.pkl'
scaler_path = 'scaler.pkl'

if not os.path.exists(model_path) or not os.path.exists(scaler_path):
    raise FileNotFoundError("Model or scaler file is missing. Ensure 'model.pkl' and 'scaler.pkl' exist in the directory.")

with open(model_path, 'rb') as model_file:
    model = pickle.load(model_file)
with open(scaler_path, 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# OpenWeatherMap Configuration
API_KEY = "9de703cd976588442a2d1ee0cba814a2"
CITY = "visakhapatnam"
WEATHER_API_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

def fetch_weather_data():
    try:
        response = requests.get(WEATHER_API_URL)
        data = response.json()

        weather_features = {
            "pressure": data["main"]["pressure"],
            "temperature": data["main"]["temp"],
            "dewpoint": data["main"]["temp_min"],
            "humidity": data["main"]["humidity"],
            "cloud": data["clouds"]["all"],
            "sunshine": 100 - data["clouds"]["all"],
            "winddirection": data["wind"]["deg"],
            "windspeed": data["wind"]["speed"]
        }
        return weather_features

    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['GET'])
def predict_today():
    try:
        weather_data = fetch_weather_data()

        if "error" in weather_data:
            return jsonify({"error": weather_data["error"]})

        features = np.array(list(weather_data.values())).reshape(1, -1)
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        prediction_text = 'Rain' if prediction == 1 else 'No Rain'

        return render_template('index.html', prediction=prediction_text, weather_data=weather_data)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
