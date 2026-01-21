import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

# Load NASA CSV (skip metadata rows)
df = pd.read_csv("data/nasa_weather.csv", skiprows=10)

# Select required columns
df = df[["RH2M", "T2M"]]

# Handle missing values automatically
df.replace(-999, np.nan, inplace=True)
df.dropna(inplace=True)

# Create shelf-life target (science-based)
df["shelf_life_days"] = (
    90
    - 0.6 * df["RH2M"]
    - 0.3 * df["T2M"]
)

df["shelf_life_days"] = df["shelf_life_days"].clip(lower=0)

# Train model
X = df[["RH2M", "T2M"]]
y = df["shelf_life_days"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "shelf_life_model.pkl")

print("✅ Shelf-life model trained successfully")