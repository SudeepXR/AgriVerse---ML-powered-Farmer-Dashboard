import csv
import os
import math
import sys

# Adjust path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.config import (
    RAW_DIR, PROCESSED_DIR,
    RAW_TRAINING_FILE, RAW_REGIONAL_FILE, RAW_HISTORICAL_FILE,
    RAW_WEATHER_HISTORICAL_FILE,
    PROCESSED_TRAINING_FILE, REGIONAL_PROFILES_FILE, SEASONALITY_FILE
)

# ==========================================
# CONFIGURATION (Derived from config.py)
# ==========================================

FILES = {
    "training": RAW_TRAINING_FILE,
    "regional": RAW_REGIONAL_FILE,
    "historical": RAW_HISTORICAL_FILE,
    "weather_historical": RAW_WEATHER_HISTORICAL_FILE
}

OUTPUTS = {
    "training_clean": PROCESSED_TRAINING_FILE,
    "regional_profiles": REGIONAL_PROFILES_FILE,
    "seasonality": SEASONALITY_FILE
}

# ==========================================
# HELPER FUNCTIONS (Deterministic & Safe)
# ==========================================

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def read_csv(filename):
    path = os.path.join(RAW_DIR, filename)
    if not os.path.exists(path):
        print(f"ERROR: Missing file {path}")
        sys.exit(1)
    
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return data

def write_csv(filename, fieldnames, rows):
    path = os.path.join(PROCESSED_DIR, filename)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {path}")

def parse_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def parse_percentage(value_str):
    """
    Parses strings like '96.42%' or '0.03%' to float 0.9642, 0.0003.
    Returns 0.0 if parse fails.
    """
    if not value_str:
        return 0.0
    clean = value_str.replace('%', '').strip()
    try:
        # The raw data seems to be '96.42%' meaning 96.42 out of 100.
        # We want to use it as a weight (0-1).
        return float(clean) / 100.0
    except ValueError:
        return 0.0

def calculate_tertile_means(values):
    """
    Splits a list of floats into 3 chunks (Low, Medium, High)
    and returns the mean of each chunk.
    Used to derive representative values for N/P/K imputation.
    """
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 0:
        return 0, 0, 0
    
    # Simple equal-count split
    chunk_size = n // 3
    
    low_chunk = sorted_vals[:chunk_size]
    # If not perfectly divisible, put remainder in middle or split? 
    # Simple approach: roughly 33/33/33
    mid_chunk = sorted_vals[chunk_size : 2*chunk_size]
    high_chunk = sorted_vals[2*chunk_size:]
    
    def mean(lst):
        return sum(lst) / len(lst) if lst else 0
        
    return mean(low_chunk), mean(mid_chunk), mean(high_chunk)

# ==========================================
# PROCESSING LOGIC
# ==========================================

def process_training_data():
    """
    1. Loads Crop_recommendation.csv
    2. Validates types
    3. Calculates Low/Med/High representatives for Imputation logic
    4. Calculates Crop-wise average weather (Temp, Hum, Rain)
    5. Saves clean training file
    """
    print("Processing Training Data...")
    raw_data = read_csv(FILES["training"])
    
    clean_rows = []
    
    # Collectors for stats
    n_values = []
    p_values = []
    k_values = []
    ph_values = []
    
    # Crop-wise weather accumulator: crop -> {'temp': [], 'hum': [], 'rain': []}
    crop_weather_acc = {}

    for row in raw_data:
        try:
            n = parse_float(row['N'])
            p = parse_float(row['P'])
            k = parse_float(row['K'])
            ph = parse_float(row['ph'])
            
            n_values.append(n)
            p_values.append(p)
            k_values.append(k)
            ph_values.append(ph)
            
            temp = parse_float(row['temperature'])
            hum = parse_float(row['humidity'])
            rain = parse_float(row['rainfall'])
            label = row['label'].strip().lower()

            clean_row = {
                'N': n,
                'P': p,
                'K': k,
                'temperature': temp,
                'humidity': hum,
                'ph': ph,
                'rainfall': rain,
                'label': label
            }
            clean_rows.append(clean_row)
            
            # Accumulate weather stats
            if label not in crop_weather_acc:
                crop_weather_acc[label] = {'temp': [], 'hum': [], 'rain': []}
            crop_weather_acc[label]['temp'].append(temp)
            crop_weather_acc[label]['hum'].append(hum)
            crop_weather_acc[label]['rain'].append(rain)

        except Exception as e:
            print(f"Skipping training row due to error: {e}")
            continue

    # Calculate Representatives (The Bridge between Training and Inference)
    n_reps = calculate_tertile_means(n_values)
    p_reps = calculate_tertile_means(p_values)
    k_reps = calculate_tertile_means(k_values)
    ph_reps = calculate_tertile_means(ph_values)
    
    # Calculate Crop Weather Profiles
    crop_weather_profiles = {}
    for crop, stats in crop_weather_acc.items():
        crop_weather_profiles[crop] = {
            'avg_temp': sum(stats['temp']) / len(stats['temp']) if stats['temp'] else 25.0,
            'avg_hum': sum(stats['hum']) / len(stats['hum']) if stats['hum'] else 70.0,
            'avg_rain': sum(stats['rain']) / len(stats['rain']) if stats['rain'] else 100.0
        }

    print(f"  Heuristic Stats (Low/Med/High Means):")
    print(f"  N: {n_reps}")
    print(f"  P: {p_reps}")
    print(f"  K: {k_reps}")
    print(f"  pH: {ph_reps}")
    print(f"  Derived Weather Profiles for {len(crop_weather_profiles)} crops.")
    
    write_csv(OUTPUTS["training_clean"], 
              ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label'], 
              clean_rows)
              
    return n_reps, p_reps, k_reps, ph_reps, crop_weather_profiles


def process_weather_historical_data():
    """
    Processes Custom_Crops_yield_Historical_Dataset.csv to extract
    district-level long-term climate averages.
    
    Returns: dict mapping District (lowercase) -> {avg_temp, avg_hum, avg_rain}
    """
    print("Processing Weather Historical Data...")
    raw_data = read_csv(FILES["weather_historical"])
    
    # Accumulate by district
    district_weather = {}  # district -> {temps: [], hums: [], rains: []}
    
    for row in raw_data:
        dist_name = row.get('Dist Name', '').strip().lower()
        if not dist_name:
            continue
        
        temp = parse_float(row.get('Temperature_C'), None)
        hum = parse_float(row.get('Humidity_%'), None)
        rain = parse_float(row.get('Rainfall_mm'), None)
        
        # Skip rows with missing weather data
        if temp is None or hum is None or rain is None:
            continue
            
        if dist_name not in district_weather:
            district_weather[dist_name] = {'temps': [], 'hums': [], 'rains': []}
        
        district_weather[dist_name]['temps'].append(temp)
        district_weather[dist_name]['hums'].append(hum)
        district_weather[dist_name]['rains'].append(rain)
    
    # Calculate averages
    district_climate = {}
    for dist, data in district_weather.items():
        if data['temps']:
            district_climate[dist] = {
                'avg_temp': sum(data['temps']) / len(data['temps']),
                'avg_hum': sum(data['hums']) / len(data['hums']),
                'avg_rain': sum(data['rains']) / len(data['rains'])
            }
    
    print(f"  Derived Weather Profiles for {len(district_climate)} districts.")
    return district_climate

def process_regional_data(n_reps, p_reps, k_reps, ph_reps, crop_weather_profiles, district_climate=None):
    """
    1. Loads CropDataset-Enhanced.csv
    2. Parses percentages
    3. Imputes a single weighted average N/P/K/pH for the district
    4. Imputes average Weather from district_climate (primary) or crop_weather_profiles (fallback)
    5. Saves district profiles.
    """
    print("Processing Regional Data...")
    raw_data = read_csv(FILES["regional"])
    
    clean_rows = []
    
    for row in raw_data:
        # Parse Distribution Weights
        # Nitrogen
        n_high_w = parse_percentage(row.get('Nitrogen - High', '0'))
        n_med_w = parse_percentage(row.get('Nitrogen - Medium', '0'))
        n_low_w = parse_percentage(row.get('Nitrogen - Low', '0'))
        
        # Phosphorous
        p_high_w = parse_percentage(row.get('Phosphorous - High', '0'))
        p_med_w = parse_percentage(row.get('Phosphorous - Medium', '0'))
        p_low_w = parse_percentage(row.get('Phosphorous - Low', '0'))
        
        # Potassium
        k_high_w = parse_percentage(row.get('Potassium - High', '0'))
        k_med_w = parse_percentage(row.get('Potassium - Medium', '0'))
        k_low_w = parse_percentage(row.get('Potassium - Low', '0'))
        
        # pH
        ph_acidic_w = parse_percentage(row.get('pH - Acidic', '0'))
        ph_neutral_w = parse_percentage(row.get('pH - Neutral', '0'))
        ph_alkaline_w = parse_percentage(row.get('pH - Alkaline', '0'))

        # Normalize weights
        def norm(w1, w2, w3):
            total = w1 + w2 + w3
            if total == 0: return 0.33, 0.33, 0.33
            return w1/total, w2/total, w3/total

        nw1, nw2, nw3 = norm(n_low_w, n_med_w, n_high_w)
        pw1, pw2, pw3 = norm(p_low_w, p_med_w, p_high_w)
        kw1, kw2, kw3 = norm(k_low_w, k_med_w, k_high_w)
        phw1, phw2, phw3 = norm(ph_acidic_w, ph_neutral_w, ph_alkaline_w)

        # Calculate Imputed Soil
        imputed_n = (nw1 * n_reps[0]) + (nw2 * n_reps[1]) + (nw3 * n_reps[2])
        imputed_p = (pw1 * p_reps[0]) + (pw2 * p_reps[1]) + (pw3 * p_reps[2])
        imputed_k = (kw1 * k_reps[0]) + (kw2 * k_reps[1]) + (kw3 * k_reps[2])
        imputed_ph = (phw1 * ph_reps[0]) + (phw2 * ph_reps[1]) + (phw3 * ph_reps[2])

        # Extract feasible crops list
        crops_str = row.get('Crop', '')
        crops_list = [c.strip() for c in crops_str.split(',') if c.strip()]
        
        # Calculate Imputed Weather
        # Priority 1: Use district-level climate from historical dataset
        district_key = row.get('Address', '').strip().lower()
        climate_profile = district_climate.get(district_key) if district_climate else None
        
        if climate_profile:
            # Use real historical climate data for this district
            imp_temp = climate_profile['avg_temp']
            imp_hum = climate_profile['avg_hum']
            imp_rain = climate_profile['avg_rain']
        else:
            # Fallback: Average of crop weather profiles for feasible crops
            temps, hums, rains = [], [], []
            for c in crops_list:
                profile = crop_weather_profiles.get(c.lower())
                if not profile:
                    for known_crop, known_profile in crop_weather_profiles.items():
                        if known_crop in c.lower() or c.lower() in known_crop:
                            profile = known_profile
                            break
                if profile:
                    temps.append(profile['avg_temp'])
                    hums.append(profile['avg_hum'])
                    rains.append(profile['avg_rain'])
            
            imp_temp = sum(temps)/len(temps) if temps else 25.0
            imp_hum = sum(hums)/len(hums) if hums else 70.0
            imp_rain = sum(rains)/len(rains) if rains else 100.0

        crops_clean_str = "|".join(crops_list)

        clean_row = {
            'District': row.get('Address', '').strip(),
            'State': row.get('Region', '').strip(),
            'Imputed_N': round(imputed_n, 2),
            'Imputed_P': round(imputed_p, 2),
            'Imputed_K': round(imputed_k, 2),
            'Imputed_pH': round(imputed_ph, 2),
            'Imputed_Temp': round(imp_temp, 2),
            'Imputed_Hum': round(imp_hum, 2),
            'Imputed_Rain': round(imp_rain, 2),
            'Feasible_Crops': crops_clean_str
        }
        clean_rows.append(clean_row)

    write_csv(OUTPUTS["regional_profiles"], 
              ['District', 'State', 'Imputed_N', 'Imputed_P', 'Imputed_K', 'Imputed_pH', 
               'Imputed_Temp', 'Imputed_Hum', 'Imputed_Rain', 'Feasible_Crops'], 
              clean_rows)

def process_historical_data():
    """
    1. Loads crop_production.csv
    2. Cleans Season (trim whitespace)
    3. Normalizes District names
    4. Creates a set of verified (District, Season, Crop) tuples.
    """
    print("Processing Historical Data...")
    raw_data = read_csv(FILES["historical"])
    
    # Use a set to store unique combinations
    unique_entries = set()
    
    for row in raw_data:
        dist = row['District_Name'].strip().title() # "NICOBARS" -> "Nicobars"
        season = row['Season'].strip() # "Kharif     " -> "Kharif"
        crop = row['Crop'].strip()
        
        # Skip garbage
        if not dist or not season or not crop:
            continue
            
        unique_entries.add((dist, season, crop))
        
    # Convert to list of dicts
    clean_rows = []
    for d, s, c in sorted(list(unique_entries)):
        clean_rows.append({
            'District': d,
            'Season': s,
            'Crop': c
        })
        
    write_csv(OUTPUTS["seasonality"], 
              ['District', 'Season', 'Crop'], 
              clean_rows)

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    print("Starting Feature Engineering Pipeline (Deterministic)...")
    ensure_dir(PROCESSED_DIR)
    
    # Step 1: Process Training Data & Get Heuristics
    n_reps, p_reps, k_reps, ph_reps, crop_profiles = process_training_data()
    
    # Step 2: Process Weather Historical Data (District Climate)
    district_climate = process_weather_historical_data()
    
    # Step 3: Process Regional Data using Heuristics + District Climate
    process_regional_data(n_reps, p_reps, k_reps, ph_reps, crop_profiles, district_climate)
    
    # Step 4: Process Historical/Seasonality Data
    process_historical_data()
    
    print("Feature Engineering Complete.")
    print(f"Outputs available in {PROCESSED_DIR}")

if __name__ == "__main__":
    main()
