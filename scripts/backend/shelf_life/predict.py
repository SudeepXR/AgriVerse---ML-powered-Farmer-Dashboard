import joblib
import requests
from datetime import datetime, date
import sys
import os
import numpy as np

# --------------------------------------------------
# DISTRICT → COORDINATES
# --------------------------------------------------

DISTRICT_COORDS = {
    "BANGALORE": (12.9716, 77.5946),
    "MYSORE": (12.2958, 76.6394),
    "MANDYA": (12.5235, 76.8970),
    "HASSAN": (13.0072, 76.0962),
    "TUMKUR": (13.3409, 77.1010),
    "DAVANAGERE": (14.4663, 75.9240),
    "SHIMOGA": (13.9299, 75.5681),
    "BELGAUM": (15.8497, 74.4977),
    "BELLARY": (15.1394, 76.9214),
}

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "shelf_life_model.pkl")

try:
    model = joblib.load(model_path)
except FileNotFoundError:
    print(f"❌ shelf_life_model.pkl not found at {model_path}. Train model first.")
    sys.exit()

# --------------------------------------------------
# FETCH CLIMATE (HISTORICAL OR CLIMATOLOGY)
# --------------------------------------------------

def get_climate(lat, lon, target_date):
    today = date.today()
    day_of_year = target_date.timetuple().tm_yday

    # 🔹 CASE 1: Past dates → fetch exact data
    if target_date.date() < today:
        return fetch_daily_nasa(lat, lon, target_date)

    # 🔹 CASE 2: Today or future → use climatology
    return fetch_climatology(lat, lon, day_of_year)


def fetch_daily_nasa(lat, lon, target_date):
    date_str = target_date.strftime("%Y%m%d")

    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters=T2M,RH2M"
        f"&start={date_str}&end={date_str}"
        f"&latitude={lat}&longitude={lon}"
        "&community=AG&format=JSON"
    )

    r = requests.get(url, timeout=10).json()

    if "properties" not in r:
        raise ValueError("❌ No historical weather data available.")

    params = r["properties"]["parameter"]
    return params["RH2M"][date_str], params["T2M"][date_str]


def fetch_climatology(lat, lon, day_of_year):
    # Last 10 years climatology
    start_year = date.today().year - 10
    values_h, values_t = [], []

    for y in range(start_year, start_year + 10):
        d = datetime.strptime(f"{y}-01-01", "%Y-%m-%d") \
            .replace(tzinfo=None) \
            .timetuple()
        target = datetime(y, 1, 1) + \
            (datetime.strptime("2000-01-02", "%Y-%m-%d") - datetime.strptime("2000-01-01", "%Y-%m-%d")) * (day_of_year - 1)

        try:
            h, t = fetch_daily_nasa(lat, lon, target)
            values_h.append(h)
            values_t.append(t)
        except:
            continue

    if not values_h:
        raise ValueError("❌ Unable to compute climatology.")

    return np.mean(values_h), np.mean(values_t)

# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

def predict_shelf_life(harvest_date, storage_lat, storage_lon, transport_hours):
    humidity, temperature = get_climate(
        storage_lat, storage_lon, harvest_date
    )

    base_life = model.predict([[humidity, temperature]])[0]

    journey_loss = transport_hours / 6
    if humidity > 75:
        journey_loss += 2

    final_life = max(0, base_life - journey_loss)

    if final_life < 7:
        risk = "High"
    elif final_life < 20:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "humidity": round(humidity, 1),
        "temperature": round(temperature, 1),
        "base_shelf_life_days": round(base_life, 1),
        "final_shelf_life_days": round(final_life, 1),
        "risk_level": risk
    }

# --------------------------------------------------
# FARMER INPUT
# --------------------------------------------------

if __name__ == "__main__":

    print("\n🌾 FARMER INPUT")

    try:
        harvest_date = datetime.strptime(
            input("Enter harvest date (YYYY-MM-DD): "),
            "%Y-%m-%d"
        )

        storage_district = input(
            "Enter storage district: "
        ).strip().upper()

        if storage_district not in DISTRICT_COORDS:
            raise ValueError("Unsupported district.")

        transport_hours = float(
            input("Enter transport duration (hours): ")
        )

        lat, lon = DISTRICT_COORDS[storage_district]

        result = predict_shelf_life(
            harvest_date, lat, lon, transport_hours
        )

        print("\n📦 SHELF LIFE PREDICTION")
        print(f"Storage Location: {storage_district}")
        for k, v in result.items():
            print(f"{k.replace('_', ' ').title()}: {v}")

    except Exception as e:
        print("\n❌ Error:", e)