from fastapi import FastAPI
from pydantic import BaseModel, Field
from enum import Enum
import pandas as pd
import requests

# Import map generator
from farmer_map import generate_farmer_map

# ------------------ APP ------------------
app = FastAPI(
    title="Farmer Redistribution Decision API",
    description="Helps farmers decide where to send produce based on surplus, deficit & shelf life",
    version="1.0"
)

# ------------------ DATA ------------------
DATA_PATH = "../data/processed_data.csv"
SHIPMENTS_PATH = "../data/optimized_shipments_with_latlon.csv"

df = pd.read_csv(DATA_PATH)

# ------------------ ENUMS (DROPDOWNS) ------------------

class DistrictEnum(str, Enum):
    BAGALKOT = "BAGALKOT"
    BELGAUM = "BELGAUM"
    BELLARY = "BELLARY"
    BIDAR = "BIDAR"
    BIJAPUR = "BIJAPUR"
    CHITRADURGA = "CHITRADURGA"
    DAVANAGERE = "DAVANAGERE"
    GADAG = "GADAG"
    GULBARGA = "GULBARGA"
    HASSAN = "HASSAN"
    HAVERI = "HAVERI"
    KOPPAL = "KOPPAL"
    MANDYA = "MANDYA"
    RAICHUR = "RAICHUR"
    SHIMOGA = "SHIMOGA"
    TUMKUR = "TUMKUR"
    UTTARA_KANNADA = "UTTARA KANNADA"
    BANGALORE = "BANGALORE"
    BANGALORE_RURAL = "BANGALORE RURAL"
    MYSORE = "MYSORE"
    DAKSHINA_KANNADA = "DAKSHINA KANNADA"
    UDUPI = "UDUPI"
    KOLAR = "KOLAR"


class GrainEnum(str, Enum):
    RICE = "rice"
    WHEAT = "wheat"
    MAIZE = "maize"
    MILLET = "millet"
    PULSES = "pulses"


class StorageEnum(str, Enum):
    OPEN = "open"
    WAREHOUSE = "warehouse"
    COLD_STORAGE = "cold_storage"


# ------------------ INPUT MODEL ------------------

class FarmerInput(BaseModel):
    district: DistrictEnum
    grain: GrainEnum
    storage_type: StorageEnum
    produce_tons: float = Field(
        ge=0.1,
        le=10000,
        description="Amount of produce in tons"
    )

# ------------------ METADATA ENDPOINT ------------------

@app.get("/metadata")
def get_metadata():
    return {
        "districts": [d.value for d in DistrictEnum],
        "grains": [g.value for g in GrainEnum],
        "storage_types": [s.value for s in StorageEnum],
        "produce_range_tons": [0.1, 10000]
    }

# ------------------ FARMER REDISTRIBUTION API ------------------

@app.post("/farmer/redistribution")
def farmer_redistribution(data: FarmerInput):

    district = data.district.value
    produce = data.produce_tons

    # Get farmer district row
    farmer_row = df[df["District_Name"] == district].iloc[0]

    # Add farmer produce to local surplus
    available = farmer_row["Surplus_tons"] + produce

    # Get deficit districts
    deficit_df = df[df["Deficit_tons"] > 0].copy()

    if deficit_df.empty:
        return {
            "message": "No deficit districts currently. Store or sell locally.",
            "available_tons": available
        }

    # Choose district with highest deficit
    target = deficit_df.sort_values(
        by="Deficit_tons", ascending=False
    ).iloc[0]

    # ------------------ MAP GENERATION ------------------
    map_path = "../data/farmer_map.html"

    generate_farmer_map(
        farmer_district=district,
        target_district=target["District_Name"],
        shipments_csv=SHIPMENTS_PATH,
        output_map_path=map_path
    )

    # ------------------ SHELF LIFE API ------------------
    shelf_response = requests.post(
        "http://127.0.0.1:8000/predict",
        json={
            "temperature": 32,   # can be auto-fetched later
            "humidity": 75,
            "grain": data.grain.value
        }
    ).json()

    send_amount = min(produce, target["Deficit_tons"])

    return {
        "farmer_district": district,
        "grain": data.grain.value,
        "storage_type": data.storage_type.value,
        "produce_tons": produce,
        "recommended_destination": target["District_Name"],
        "send_tons": round(send_amount, 2),
        "urgency": shelf_response["risk_level"],
        "confidence": shelf_response["confidence"],
        "redistribution_advice": (
            "Send immediately"
            if shelf_response["trigger_redistribution"]
            else "Normal priority"
        ),
        "map_file": "farmer_map.html"
    }
