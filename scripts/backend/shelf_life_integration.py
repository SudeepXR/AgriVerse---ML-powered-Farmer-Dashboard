import os
import joblib
import numpy as np
import requests
from datetime import datetime, timedelta

# District mapping (Same as app.py)
KARNATAKA_DISTRICTS = {
    "Bengaluru Urban": {"lat": 12.9716, "lon": 77.5946},
    "Bengaluru Rural": {"lat": 13.2846, "lon": 77.6070},
    "Mysuru": {"lat": 12.2958, "lon": 76.6394},
    "Mandya": {"lat": 12.5223, "lon": 76.8974},
    "Tumakuru": {"lat": 13.3392, "lon": 77.1130},
    "Hassan": {"lat": 13.0068, "lon": 76.0996},
    "Shivamogga": {"lat": 13.9299, "lon": 75.5681},
    "Chitradurga": {"lat": 14.2306, "lon": 76.3986},
    "Davanagere": {"lat": 14.4644, "lon": 75.9218},
    "Ballari": {"lat": 15.1394, "lon": 76.9214},
    "Vijayapura": {"lat": 16.8302, "lon": 75.7100},
    "Belagavi": {"lat": 15.8497, "lon": 74.4977},
    "Dharwad": {"lat": 15.4589, "lon": 75.0078},
    "Kalaburagi": {"lat": 17.3297, "lon": 76.8343},
    "Raichur": {"lat": 16.2076, "lon": 77.3463},
    "Bidar": {"lat": 17.9149, "lon": 77.5046},
    "Kolar": {"lat": 13.1357, "lon": 78.1326},
    "Chikkaballapur": {"lat": 13.4355, "lon": 77.7315},
    "Udupi": {"lat": 13.3409, "lon": 74.7421},
    "Dakshina Kannada": {"lat": 12.8438, "lon": 75.2479},
    "Kodagu": {"lat": 12.3375, "lon": 75.8069}
}

class ShelfLifeModel:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        try:
            # Assumes this file is in scripts/backend/
            base_path = os.path.dirname(os.path.abspath(__file__))
            # Adjusted path to reach shelf_life/shelf_life_model.pkl
            model_path = os.path.join(base_path, "shelf_life", "shelf_life_model.pkl")
            self.model = joblib.load(model_path)
            print(f"✅ Shelf life model loaded from {model_path}")
        except Exception as e:
            print(f"⚠️ Failed to load shelf life model: {e}")
            self.model = None

    def get_weather_forecast(self, lat, lon):
        """
        Fetch current weather/forecast from Open-Meteo (Simpler and faster than NASA for demo)
        """
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m"],
                "timezone": "auto"
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Use current conditions for shelf life prediction
            temp = data["current"]["temperature_2m"]
            humidity = data["current"]["relative_humidity_2m"]
            
            return temp, humidity
        except Exception as e:
            print(f"Error fetching weather: {e}")
            # Fallback values (Average for Karnataka)
            return 28.0, 65.0

    def predict(self, district_name, harvest_date_str, transport_hours):
        if not self.model:
            return {"error": "Model not loaded"}

        # Normalize district name
        # Try to find case-insensitive match
        district_key = None
        for key in KARNATAKA_DISTRICTS:
            if key.lower() == district_name.lower():
                district_key = key
                break
        
        if not district_key:
            # Basic fuzzy match or fallback
            district_key = "Bengaluru Urban" # Default
        
        coords = KARNATAKA_DISTRICTS[district_key]
        
        # 1. Get Weather (Temperature & Humidity)
        # Note: Ideally we would look up historical weather for the specific harvest date
        # But for this integrated dashboard, using current conditions/forecast is often preferred for "Real-time" feel
        # unless the user picks a far past date.
        
        temperature, humidity = self.get_weather_forecast(coords["lat"], coords["lon"])
        
        # 2. Predict Base Shelf Life
        # Model expects [[RH, Temp]]
        base_life_days = self.model.predict([[humidity, temperature]])[0]
        
        # 3. Adjust for Transport
        journey_loss = float(transport_hours) / 6.0
        if humidity > 75:
            journey_loss += 2.0  # High humidity penalty
            
        final_life_days = max(0, base_life_days - journey_loss)
        
        # 4. Determine Risk
        if final_life_days < 3:
            risk = "Critical"
        elif final_life_days < 7:
            risk = "High"
        elif final_life_days < 15:
            risk = "Medium"
        else:
            risk = "Low"
            
        return {
            "district": district_key,
            "harvest_date": harvest_date_str,
            "weather_used": {
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1)
            },
            "prediction": {
                "base_shelf_life_days": round(base_life_days, 1),
                "final_shelf_life_days": round(final_life_days, 1),
                "risk_level": risk,
                "transport_impact_days": round(journey_loss, 1)
            }
        }

# Singleton instance
shelf_life_service = ShelfLifeModel()