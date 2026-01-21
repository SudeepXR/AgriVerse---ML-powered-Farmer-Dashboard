import uvicorn
import joblib
import numpy as np
from fastapi import FastAPI
import os
from tensorflow.keras.models import load_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "global_lstm.h5")

print("Loading model from:", MODEL_PATH)

lstm = load_model(MODEL_PATH, compile=False)

# =====================================================
# CONFIG
# =====================================================
LOOKBACK = 60
SHORT_DAYS = 7
LONG_MONTHS = 3

# =====================================================
# LOAD MODELS & CACHED DATA (NO CSV)
# =====================================================
MODELS_DIR = os.path.join(BASE_DIR, "models")

xgb = joblib.load(os.path.join(MODELS_DIR, "global_xgb.pkl"))
scaler = joblib.load(os.path.join(MODELS_DIR, "global_scaler.pkl"))
district_enc = joblib.load(os.path.join(MODELS_DIR, "district_encoder.pkl"))
commodity_enc = joblib.load(os.path.join(MODELS_DIR, "commodity_encoder.pkl"))
recent_daily = joblib.load(os.path.join(MODELS_DIR, "recent_history.pkl"))
recent_monthly = joblib.load(os.path.join(MODELS_DIR, "recent_monthly.pkl"))

# app = FastAPI(title="Agri Price Forecast API (No CSV)")

# =====================================================
# METADATA ENDPOINTS
# =====================================================
# @app.get("/districts")
# def get_districts():
#     return {"districts": sorted(district_enc.keys())}


# @app.get("/commodities/{district}")
# def get_commodities(district: str):
#     district = district.strip().title()
#     commodities = sorted({
#         c for (d, c) in recent_daily.keys() if d == district
#     })
#     return {"commodities": commodities}


def predict(district: str, commodity: str):

    district = district.strip().title()
    commodity = commodity.strip().title()

    # ---------------------------
    # VALIDATION
    # ---------------------------
    if district not in district_enc:
        return {"error": f"Unknown district: {district}"}

    if commodity not in commodity_enc:
        return {"error": f"Unknown commodity: {commodity}"}

    key = (district, commodity)

    if key not in recent_daily or len(recent_daily[key]) < LOOKBACK:
        return {"error": "Not enough recent daily data"}

    # =====================================================
    # SHORT-TERM FORECAST (GLOBAL LSTM)
    # =====================================================
    prices = np.array(recent_daily[key][-LOOKBACK:]).reshape(-1, 1)
    current_price = float(prices[-1][0])

    prices_scaled = scaler.transform(prices)

    d_id = district_enc[district]
    c_id = commodity_enc[commodity]
    month = 1  # fixed (can be replaced with current month later)

    meta = np.array([d_id, c_id, month], dtype=np.float32)
    meta_seq = np.repeat(meta[np.newaxis, :], LOOKBACK, axis=0)

    seq = prices_scaled.copy()
    X = np.concatenate([seq, meta_seq], axis=1).reshape(1, LOOKBACK, 4)

    short_scaled = []

    for _ in range(SHORT_DAYS):
        p = lstm.predict(X, verbose=0)[0, 0]
        short_scaled.append(p)

        seq = np.vstack([seq[1:], [[p]]])
        X = np.concatenate([seq, meta_seq], axis=1).reshape(1, LOOKBACK, 4)

    short_forecast = scaler.inverse_transform(
        np.array(short_scaled).reshape(-1, 1)
    ).flatten()

    # =====================================================
    # MEDIUM-TERM FORECAST (GLOBAL XGBOOST)
    # =====================================================
    long_forecast = []

    if key in recent_monthly and len(recent_monthly[key]) >= 3:
        lags = recent_monthly[key][-3:]

        for i in range(LONG_MONTHS):
            Xg = [[
                lags[-1],
                lags[-2],
                lags[-3],
                i + 1,
                d_id,
                c_id
            ]]
            p = float(xgb.predict(Xg)[0])
            long_forecast.append(p)
            lags = lags[1:] + [p]

    # =====================================================
    # FARMER ADVISORY
    # =====================================================
    advisory = []
    avg_short = np.mean(short_forecast)

    if avg_short > current_price * 1.05:
        advisory.append("Short-term: Prices likely to rise. Holding is advised.")
    elif avg_short < current_price * 0.95:
        advisory.append("Short-term: Prices may fall. Consider selling.")
    else:
        advisory.append("Short-term: Prices appear stable.")

    if long_forecast:
        avg_long = np.mean(long_forecast)
        if avg_long > current_price * 1.10:
            advisory.append("Long-term: Favorable conditions for planting.")
        elif avg_long < current_price * 0.90:
            advisory.append("Long-term: Caution advised for new planting.")
        else:
            advisory.append("Long-term: Stable outlook.")

    # =====================================================
    # RESPONSE
    # =====================================================
    return {
        "current_price": current_price,
        "short_term_forecast": {
            f"Day {i+1}": float(v) for i, v in enumerate(short_forecast)
        },
        "medium_term_forecast": {
            f"Month +{i+1}": float(v) for i, v in enumerate(long_forecast)
        },
        "farmer_advisory": advisory
    }



