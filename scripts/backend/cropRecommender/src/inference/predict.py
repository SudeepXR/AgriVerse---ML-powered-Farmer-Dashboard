import sys
import os
import json
import pickle
import numpy as np
import jsonschema
import csv

# Adjust path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.explainability.generate_reasons import generate_reasons
from src.inference.degradation import DegradationLevel, get_confidence_cap, get_coverage_meta
from src.config import (
    ARTIFACTS_DIR, METADATA_DIR, SCHEMA_PATH,
    PROCESSED_DIR, REGIONAL_PROFILES_FILE, SEASONALITY_FILE, PROCESSED_TRAINING_FILE,
    FEATURES,
    HIGH_CONFIDENCE_THRESHOLD, MEDIUM_CONFIDENCE_THRESHOLD
)

# ==========================================
# CONFIGURATION (Derived from config.py)
# ==========================================

REGIONAL_PROFILES_PATH = os.path.join(PROCESSED_DIR, REGIONAL_PROFILES_FILE)
SEASONALITY_LOG_PATH = os.path.join(PROCESSED_DIR, SEASONALITY_FILE)
TRAINING_DATA_PATH = os.path.join(PROCESSED_DIR, PROCESSED_TRAINING_FILE)

# Defined in Step 6 / 3 Canon - now sourced from config
FEATURES_ORDER = FEATURES

# Global Cache
_REGIONAL_PROFILES = None
_SEASONALITY_LOG = None
_GLOBAL_WEATHER_STATS = None

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def load_schema():
    """Loads the output JSON schema for validation."""
    if not os.path.exists(SCHEMA_PATH):
        raise RuntimeError(f"Schema not found at {SCHEMA_PATH}")
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)

def validate_output(response, schema):
    """
    Validates the response against the schema.
    Raises jsonschema.ValidationError if invalid.
    """
    jsonschema.validate(instance=response, schema=schema)

def load_latest_model_and_meta():
    """
    Loads the most recent model artifact and its metadata.
    """
    if not os.path.exists(ARTIFACTS_DIR):
        raise RuntimeError("Model artifacts directory missing.")
        
    files = [f for f in os.listdir(ARTIFACTS_DIR) if f.endswith('.pkl')]
    if not files:
        raise RuntimeError("No model artifacts found. Train the model first.")
        
    # Sort by name (timestamp)
    latest_model_file = sorted(files)[-1]
    
    # Find matching metadata
    timestamp_part = latest_model_file.replace('model_', '').replace('.pkl', '')
    meta_file = f"meta_{timestamp_part}.json"
    
    model_path = os.path.join(ARTIFACTS_DIR, latest_model_file)
    meta_path = os.path.join(METADATA_DIR, meta_file)
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
        
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
            
    return model, meta

def validate_input(payload):
    """
    Validates input JSON against the Phase 0 Contract.
    Enforces strict numeric ranges.
    """
    if not payload:
        raise ValueError("Empty request payload.")
        
    user_context = payload.get('user_context')
    if not user_context:
        raise ValueError("Missing 'user_context' field.")
        
    if not user_context.get('region_id'):
        raise ValueError("Missing 'region_id' in user_context.")
        
    soil_data = payload.get('soil_data')
    if soil_data:
        required_soil = ['nitrogen', 'phosphorus', 'potassium', 'ph']
        for k in required_soil:
            if k not in soil_data:
                raise ValueError(f"Partial soil_data provided. Missing '{k}'. Provide all or none.")
        
        # Range Validation - Soil
        n = soil_data.get('nitrogen', 0)
        p = soil_data.get('phosphorus', 0)
        k = soil_data.get('potassium', 0)
        ph = soil_data.get('ph', 0)

        if not (0 <= n <= 300): raise ValueError(f"Nitrogen {n} out of range (0-300)")
        if not (0 <= p <= 300): raise ValueError(f"Phosphorus {p} out of range (0-300)")
        if not (0 <= k <= 300): raise ValueError(f"Potassium {k} out of range (0-300)")
        if not (0 <= ph <= 14): raise ValueError(f"pH {ph} out of range (0-14)")

    # Range Validation - Weather (Optional per PRD FR-1)
    weather_data = payload.get('weather_data')
    if weather_data:
        required_weather = ['temperature', 'humidity', 'rainfall']
        for k in required_weather:
            if k not in weather_data:
                raise ValueError(f"Partial weather_data provided. Missing '{k}'.")
                
        temp = weather_data.get('temperature', 0)
        hum = weather_data.get('humidity', 0)
        rain = weather_data.get('rainfall', 0)
        
        if not (-10 <= temp <= 60): raise ValueError(f"Temperature {temp} out of range (-10 to 60)")
        if not (0 <= hum <= 100): raise ValueError(f"Humidity {hum} out of range (0-100)")
        if not (0 <= rain <= 10000): raise ValueError(f"Rainfall {rain} out of range (0-10000)")

    return True

def load_regional_data():
    """
    Lazy loads regional profiles and computes State/Global aggregates.
    Returns a dict with 'districts', 'states', and 'global'.
    Updated to handle Weather Imputation fields.
    """
    global _REGIONAL_PROFILES
    if _REGIONAL_PROFILES is not None:
        return _REGIONAL_PROFILES
    
    districts = {}
    states = {}
    # Accumulators for Soil and Weather
    global_accum = {
        'N': [], 'P': [], 'K': [], 'pH': [], 
        'Temp': [], 'Hum': [], 'Rain': [],
        'crops': set()
    }
    
    if os.path.exists(REGIONAL_PROFILES_PATH):
        with open(REGIONAL_PROFILES_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 1. District Level
                dist_key = row['District'].strip()
                state_key = row['State'].strip()
                
                # Parse Crops
                crops = [c.strip().lower() for c in row['Feasible_Crops'].split('|') if c.strip()]
                crop_set = set(crops)
                
                # Parse Soil & Weather
                try:
                    n = float(row['Imputed_N'])
                    p = float(row['Imputed_P'])
                    k = float(row['Imputed_K'])
                    ph = float(row['Imputed_pH'])
                    
                    # New Weather Fields (Robust get with default if missing)
                    temp = float(row.get('Imputed_Temp', 25.0))
                    hum = float(row.get('Imputed_Hum', 70.0))
                    rain = float(row.get('Imputed_Rain', 100.0))
                except ValueError:
                    continue # Skip malformed rows
                
                districts[dist_key] = {
                    'state': state_key,
                    'crops': crop_set,
                    'nitrogen': n,
                    'phosphorus': p,
                    'potassium': k,
                    'ph': ph,
                    'temperature': temp,
                    'humidity': hum,
                    'rainfall': rain
                }

                # Robust Indexing: Index simple district name if unique
                # e.g. "Satara" from "Satara, Maharashtra"
                if ',' in dist_key:
                    simple_name = dist_key.split(',')[0].strip()
                    if simple_name not in districts:
                        districts[simple_name] = districts[dist_key]
                
                # 2. State Level Aggregation
                if state_key not in states:
                    states[state_key] = {
                        'N': [], 'P': [], 'K': [], 'pH': [], 
                        'Temp': [], 'Hum': [], 'Rain': [],
                        'crops': set()
                    }
                
                states[state_key]['N'].append(n)
                states[state_key]['P'].append(p)
                states[state_key]['K'].append(k)
                states[state_key]['pH'].append(ph)
                states[state_key]['Temp'].append(temp)
                states[state_key]['Hum'].append(hum)
                states[state_key]['Rain'].append(rain)
                states[state_key]['crops'].update(crop_set)
                
                # 3. Global Level Aggregation
                global_accum['N'].append(n)
                global_accum['P'].append(p)
                global_accum['K'].append(k)
                global_accum['pH'].append(ph)
                global_accum['Temp'].append(temp)
                global_accum['Hum'].append(hum)
                global_accum['Rain'].append(rain)
                global_accum['crops'].update(crop_set)
    
    # Finalize Aggregates (Averages)
    final_states = {}
    for s, data in states.items():
        if data['N']:
            final_states[s] = {
                'nitrogen': sum(data['N']) / len(data['N']),
                'phosphorus': sum(data['P']) / len(data['P']),
                'potassium': sum(data['K']) / len(data['K']),
                'ph': sum(data['pH']) / len(data['pH']),
                'temperature': sum(data['Temp']) / len(data['Temp']),
                'humidity': sum(data['Hum']) / len(data['Hum']),
                'rainfall': sum(data['Rain']) / len(data['Rain']),
                'crops': data['crops']
            }
            
    final_global = {
        'nitrogen': sum(global_accum['N']) / len(global_accum['N']) if global_accum['N'] else 90.0,
        'phosphorus': sum(global_accum['P']) / len(global_accum['P']) if global_accum['P'] else 42.0,
        'potassium': sum(global_accum['K']) / len(global_accum['K']) if global_accum['K'] else 43.0,
        'ph': sum(global_accum['pH']) / len(global_accum['pH']) if global_accum['pH'] else 6.5,
        'temperature': sum(global_accum['Temp']) / len(global_accum['Temp']) if global_accum['Temp'] else 25.0,
        'humidity': sum(global_accum['Hum']) / len(global_accum['Hum']) if global_accum['Hum'] else 70.0,
        'rainfall': sum(global_accum['Rain']) / len(global_accum['Rain']) if global_accum['Rain'] else 100.0,
        'crops': global_accum['crops']
    }

    _REGIONAL_PROFILES = {
        'districts': districts,
        'states': final_states,
        'global': final_global
    }
    return _REGIONAL_PROFILES

def load_seasonality_data():
    """Lazy loads seasonality data."""
    global _SEASONALITY_LOG
    if _SEASONALITY_LOG is not None:
        return _SEASONALITY_LOG
    
    season_map = {}
    if os.path.exists(SEASONALITY_LOG_PATH):
        with open(SEASONALITY_LOG_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                district = row['District'].strip().lower()
                season = row['Season'].strip().lower()
                crop = row['Crop'].strip().lower()
                
                key = (district, season)
                if key not in season_map:
                    season_map[key] = set()
                season_map[key].add(crop)
                
    _SEASONALITY_LOG = season_map
    return season_map

def load_global_weather_stats():
    """
    Computes/Loads global averages for weather from the training dataset.
    Used as the safe fallback when local weather data is missing.
    """
    global _GLOBAL_WEATHER_STATS
    if _GLOBAL_WEATHER_STATS is not None:
        return _GLOBAL_WEATHER_STATS

    temps = []
    hums = []
    rains = []

    if os.path.exists(TRAINING_DATA_PATH):
        try:
            with open(TRAINING_DATA_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        temps.append(float(row['temperature']))
                        hums.append(float(row['humidity']))
                        rains.append(float(row['rainfall']))
                    except (ValueError, KeyError):
                        continue
        except Exception:
            pass # Fallback to defaults if read fails

    # Defaults if file missing or empty (Based on approximate global agg or median)
    default_temp = 25.0
    default_hum = 70.0
    default_rain = 100.0

    _GLOBAL_WEATHER_STATS = {
        'temperature': sum(temps)/len(temps) if temps else default_temp,
        'humidity': sum(hums)/len(hums) if hums else default_hum,
        'rainfall': sum(rains)/len(rains) if rains else default_rain
    }
    return _GLOBAL_WEATHER_STATS

def impute_soil_data(region_id):
    """
    Imputation Logic with Controlled Degradation.
    Returns: (soil_dict, DegradationLevel)
    """
    data = load_regional_data()
    districts = data['districts']
    states = data['states']
    global_profile = data['global']
    
    # 1. Try District
    clean_region = region_id.strip()
    if clean_region in districts:
        profile = districts[clean_region]
        return {
            'nitrogen': profile['nitrogen'],
            'phosphorus': profile['phosphorus'],
            'potassium': profile['potassium'],
            'ph': profile['ph']
        }, DegradationLevel.EXACT_REGION
        
    # 2. Try State (Parse "District, State" or just "State")
    # Attempt to split by comma
    parts = clean_region.split(',')
    potential_state = parts[-1].strip() if len(parts) > 1 else clean_region
    
    if potential_state in states:
        profile = states[potential_state]
        return {
            'nitrogen': profile['nitrogen'],
            'phosphorus': profile['phosphorus'],
            'potassium': profile['potassium'],
            'ph': profile['ph']
        }, DegradationLevel.STATE_FALLBACK
        
    # 3. Fallback to National/Global
    return {
        'nitrogen': global_profile['nitrogen'],
        'phosphorus': global_profile['phosphorus'],
        'potassium': global_profile['potassium'],
        'ph': global_profile['ph']
    }, DegradationLevel.NATIONAL_FALLBACK

def impute_weather_data(region_id):
    """
    Imputation Logic for Weather.
    
    CRITICAL ARCHITECTURE DECISION:
    The Public API explicitly forbids users from providing 'weather_data' to prevent
    hallucinated or incorrect climate inputs that could skew the model.
    Instead, we MUST derive weather parameters (Temperature, Humidity, Rainfall)
    from the 'region_id' using historical averages stored in 'regional_profiles.csv'.
    
    Degradation Hierarchy:
    1. EXACT_REGION: District-specific climate data found. (Ideal)
    2. STATE_FALLBACK: District missing, using State-level average. (Acceptable)
    3. NATIONAL_FALLBACK: Region unknown, using Global/National average. (Safety Net, Low Confidence)
    
    Returns: (weather_dict, DegradationLevel)
    """
    data = load_regional_data()
    districts = data['districts']
    states = data['states']
    global_profile = data['global']
    
    # 1. Try District
    clean_region = region_id.strip()
    if clean_region in districts:
        profile = districts[clean_region]
        return {
            'temperature': profile['temperature'],
            'humidity': profile['humidity'],
            'rainfall': profile['rainfall']
        }, DegradationLevel.EXACT_REGION
        
    # 2. Try State
    parts = clean_region.split(',')
    potential_state = parts[-1].strip() if len(parts) > 1 else clean_region
    
    if potential_state in states:
        profile = states[potential_state]
        return {
            'temperature': profile['temperature'],
            'humidity': profile['humidity'],
            'rainfall': profile['rainfall']
        }, DegradationLevel.STATE_FALLBACK

    # 3. Global Fallback
    return {
        'temperature': global_profile['temperature'],
        'humidity': global_profile['humidity'],
        'rainfall': global_profile['rainfall']
    }, DegradationLevel.NATIONAL_FALLBACK

def build_features(payload, soil_data, weather_data):
    """Constructs the feature vector."""
    # Audit: "Remove hardcoded inference features... Pass or derive features using the same pipeline as training."
    
    features = [
        soil_data['nitrogen'],
        soil_data['phosphorus'],
        soil_data['potassium'],
        weather_data['temperature'],
        weather_data['humidity'],
        soil_data['ph'],
        weather_data['rainfall']
    ]
    
    context_dict = {
        'N': features[0],
        'P': features[1],
        'K': features[2],
        'temperature': features[3],
        'humidity': features[4],
        'ph': features[5],
        'rainfall': features[6]
    }
    
    return [features], context_dict

# ==========================================
# MAIN INFERENCE PIPELINE
# ==========================================

def predict(payload):
    """
    Main Entrypoint.
    Input: JSON Dict
    Output: JSON Dict (Response)
    """
    schema = load_schema()
    
    try:
        # 1. VALIDATION
        validate_input(payload)
        
        user_context = payload['user_context']
        region_id = user_context['region_id'].strip()
        season = user_context.get('season', 'Whole Year').strip()
        
        # 2. CONTEXT & IMPUTATION
        
        # Soil Imputation
        soil_data = payload.get('soil_data')
        soil_imputation_level = DegradationLevel.EXACT_REGION
        used_imputed_soil = False

        if not soil_data:
            soil_data, soil_imputation_level = impute_soil_data(region_id)
            used_imputed_soil = True

        # Weather Imputation
        # NOTE: Users CANNOT provide weather data via API.
        # We always impute it based on the region to ensure fairness and
        # prevent 'hacking' the model with fake weather.
        weather_data = payload.get('weather_data')
        weather_imputation_level = DegradationLevel.EXACT_REGION # Default assumption
        used_imputed_weather = False

        if not weather_data:
            weather_data, weather_imputation_level = impute_weather_data(region_id)
            used_imputed_weather = True
            
        # 3. FEATURE BUILDING
        X, feature_context = build_features(payload, soil_data, weather_data)
        
        # 4. MODEL EXECUTION
        model, meta = load_latest_model_and_meta()
        classes = model.classes_
        probs = model.predict_proba(X)[0]
        
        # ==========================================
        # HYBRID PIPELINE FILTERS (FAIL-SOFT)
        # ==========================================
        
        # Load Reference Data
        all_data = load_regional_data()
        regional_profiles = all_data['districts']
        state_profiles = all_data['states']
        global_profile = all_data['global']
        seasonality_map = load_seasonality_data()
        
        # Initialize Degradation Tracking
        current_degradation = DegradationLevel.EXACT_REGION
        filter_warnings = []

        # Phase 1: Regional Feasibility Filter
        # --------------------------------------------------
        valid_regional_crops = set()
        
        # A. Try District
        if region_id in regional_profiles:
            valid_regional_crops = regional_profiles[region_id]['crops']
        else:
            # B. Try State
            parts = region_id.split(',')
            potential_state = parts[-1].strip() if len(parts) > 1 else region_id
            
            if potential_state in state_profiles:
                valid_regional_crops = state_profiles[potential_state]['crops']
                current_degradation = DegradationLevel.STATE_FALLBACK
                filter_warnings.append(f"District '{region_id}' not found. Using state-level crops ({potential_state}).")
            else:
                # C. Global Fallback
                valid_regional_crops = global_profile['crops']
                current_degradation = DegradationLevel.NATIONAL_FALLBACK
                filter_warnings.append(f"Region '{region_id}' unknown. Using national crop list.")
        
        if not valid_regional_crops:
             # Should practically never happen with global fallback
             valid_regional_crops = set(classes) # Ultimate failsafe
             filter_warnings.append("Reference data unavailable. Allowing all crops.")

        # Phase 2: Seasonal Filter
        # --------------------------------------------------
        valid_seasonal_crops = set()
        
        # 1. Normalize Inputs
        norm_season = season.lower().strip()
        norm_region = region_id.lower().strip()
        simple_district = norm_region.split(',')[0].strip()
        
        # 2. Define Lookup Helpers
        def get_crops(d_key, s_key):
            """Safe lookup in seasonality_map which is (District, Season) -> Set[Crops]"""
            return seasonality_map.get((d_key, s_key), set())

        def collect_crops_for_district(d_key):
            """Collects crops for Specific Season + Whole Year/Perennial"""
            gathered = set()
            # A. Requested Season
            gathered.update(get_crops(d_key, norm_season))
            
            # B. Perennials / All Year (Always Valid)
            gathered.update(get_crops(d_key, "whole year"))
            gathered.update(get_crops(d_key, "whole year ")) # Handle potential data dirtyness
            gathered.update(get_crops(d_key, "perennial"))
            gathered.update(get_crops(d_key, "all seasons"))
            
            return gathered

        # 3. Execution Strategy (Best Match First)
        # Strategy:
        # A. Try Exact Region ID (e.g. "satara, maharashtra")
        # B. Try Simple District (e.g. "satara")
        
        # Attempt A
        valid_seasonal_crops = collect_crops_for_district(norm_region)
        
        # Attempt B (Fallback if A yielded nothing)
        if not valid_seasonal_crops and simple_district != norm_region:
             valid_seasonal_crops = collect_crops_for_district(simple_district)
             
        # 4. Final Validation & Soft Fail
        if not valid_seasonal_crops:
            # Instead of crashing, we Open The Gates but Warn
            # Fallback to Regional Feasibility (Assume if it grows in region, it's broadly okay)
            valid_seasonal_crops = valid_regional_crops 
            filter_warnings.append(f"Seasonal data missing for '{season}' in '{region_id}'. Skipping seasonal filter.")

        # 5. RANKING & FORMATTING
        
        def filter_and_score(use_region_filter, use_season_filter):
            results = []
            
            # Determine effective degradation for this pass
            # Take the worst of: current system state, soil imputation, weather imputation
            
            # Hierarchy: NATIONAL > STATE > EXACT
            effective_level = current_degradation
            
            # Check Soil Impact
            if soil_imputation_level == DegradationLevel.NATIONAL_FALLBACK:
                effective_level = DegradationLevel.NATIONAL_FALLBACK
            elif soil_imputation_level == DegradationLevel.STATE_FALLBACK and effective_level == DegradationLevel.EXACT_REGION:
                effective_level = DegradationLevel.STATE_FALLBACK

            # Check Weather Impact
            if weather_imputation_level == DegradationLevel.NATIONAL_FALLBACK:
                effective_level = DegradationLevel.NATIONAL_FALLBACK
            elif weather_imputation_level == DegradationLevel.STATE_FALLBACK and effective_level != DegradationLevel.NATIONAL_FALLBACK:
                effective_level = DegradationLevel.STATE_FALLBACK
            
            # Determine Confidence Cap
            confidence_cap = get_confidence_cap(effective_level)
            
            for i, score in enumerate(probs):
                crop_name = classes[i]
                crop_name_lower = crop_name.lower()
                
                # 1. Region Check
                if use_region_filter:
                    is_regionally_feasible = False
                    for valid_c in valid_regional_crops:
                        if valid_c in crop_name_lower or crop_name_lower in valid_c:
                            is_regionally_feasible = True
                            break
                    if not is_regionally_feasible:
                        continue 
                    
                # 2. Season Check
                if use_season_filter:
                    is_seasonally_feasible = False
                    for valid_c in valid_seasonal_crops:
                        if valid_c in crop_name_lower or crop_name_lower in valid_c:
                            is_seasonally_feasible = True
                            break
                    if not is_seasonally_feasible:
                        continue

                # Formal Confidence Capping
                final_confidence_label = "Low"
                
                # First, map raw score to a label
                # RECALIBRATED THRESHOLDS (from config.py):
                # HIGH_CONFIDENCE_THRESHOLD = 0.70
                # MEDIUM_CONFIDENCE_THRESHOLD = 0.35
                raw_label = "Low"
                if score >= HIGH_CONFIDENCE_THRESHOLD: raw_label = "High"
                elif score >= MEDIUM_CONFIDENCE_THRESHOLD: raw_label = "Medium"
                
                # Then, apply cap
                if confidence_cap == "Low":
                    final_confidence_label = "Low"
                elif confidence_cap == "Medium":
                    if raw_label == "High": final_confidence_label = "Medium"
                    else: final_confidence_label = raw_label
                else:
                    final_confidence_label = raw_label # No cap

                results.append({
                    "crop_name": crop_name,
                    "feasibility_score": float(round(score, 2)),
                    "confidence_level": final_confidence_label
                })
            
            results.sort(key=lambda x: x['feasibility_score'], reverse=True)
            return results

        # A. Try Strict Filtering (Region + Season)
        scored_crops = filter_and_score(use_region_filter=True, use_season_filter=True)
        
        # B. Relax Season (If Empty)
        if not scored_crops:
            scored_crops = filter_and_score(use_region_filter=True, use_season_filter=False)
            if scored_crops:
                filter_warnings.append("No crops matched seasonal criteria. Showing regionally feasible options.")
        
        # C. Relax Region (If Still Empty - Fallback to Soil Match Only)
        if not scored_crops:
            # Force National Fallback state for final safety net
            current_degradation = DegradationLevel.NATIONAL_FALLBACK
            scored_crops = filter_and_score(use_region_filter=False, use_season_filter=False)
            filter_warnings.append("No crops matched regional data. Showing best soil matches.")

        # Truncate
        max_results = payload.get('request_metadata', {}).get('max_results', 5)
        top_crops = scored_crops[:max_results]
        
        # 6. EXPLANATION & META ATTACHMENT
        final_recommendations = []
        season_ctx = user_context.get('season', 'Whole Year')
        
        for rank, item in enumerate(top_crops, 1):
            expl_meta = {
                'season': season_ctx,
                'is_imputed': used_imputed_soil or used_imputed_weather,
                'score': item['feasibility_score']
            }
            
            reasons = generate_reasons(
                item['crop_name'],
                feature_context,
                metadata=expl_meta
            )
            
            item['rank'] = rank
            item['reasoning'] = reasons
            
            item['warnings'] = []
            if item['feasibility_score'] < 0.3:
                item['warnings'].append("Low feasibility score.")
            
            # Propagate System Warnings to Items (to ensure visibility)
            if filter_warnings:
                 item['warnings'].extend(filter_warnings)
                
            final_recommendations.append(item)
            
        # 7. FINAL RESPONSE CONSTRUCTION
        # Determine final degradation state for metadata
        final_degradation = current_degradation
        
        # Consolidate degradation from soil
        if soil_imputation_level == DegradationLevel.NATIONAL_FALLBACK:
            final_degradation = DegradationLevel.NATIONAL_FALLBACK
        elif soil_imputation_level == DegradationLevel.STATE_FALLBACK and final_degradation == DegradationLevel.EXACT_REGION:
            final_degradation = DegradationLevel.STATE_FALLBACK
            
        # Consolidate degradation from weather
        if weather_imputation_level == DegradationLevel.NATIONAL_FALLBACK:
            final_degradation = DegradationLevel.NATIONAL_FALLBACK
        elif weather_imputation_level == DegradationLevel.STATE_FALLBACK and final_degradation != DegradationLevel.NATIONAL_FALLBACK:
            final_degradation = DegradationLevel.STATE_FALLBACK

        # Map to Schema
        coverage = get_coverage_meta(final_degradation)
            
        disclaimer_text = "Auxiliary insight only. Not agronomic advice."
        if filter_warnings:
            disclaimer_text += f" [WARNING: {'; '.join(filter_warnings)}]"
        
        if used_imputed_soil:
            source_map = {
                DegradationLevel.EXACT_REGION: "district",
                DegradationLevel.STATE_FALLBACK: "state",
                DegradationLevel.NATIONAL_FALLBACK: "national"
            }
            source_name = source_map.get(soil_imputation_level, "unknown")
            disclaimer_text += f" [Used {source_name} soil averages]"
            
        if used_imputed_weather:
            disclaimer_text += " [Weather data was estimated from regional climate averages]"

        response = {
            "status": "success",
            "model_version": meta.get('model_version', 'unknown'),
            "meta": {
                "data_coverage": coverage,
                "used_imputed_soil_data": used_imputed_soil,  # Schema might need update for weather flag, reusing existing pattern for now
                "disclaimer": disclaimer_text
            },
            "recommendations": final_recommendations
        }
        
        # 8. OUTPUT HARDENING (RUNTIME VALIDATION)
        validate_output(response, schema)
        return response

    except ValueError as ve:
         return {
            "status": "error",
            "message": f"Input Validation Error: {str(ve)}"
        }
    except Exception as e:
        # Fail Safe Error Response
        return {
            "status": "error",
            "message": str(e)
        }

# ==========================================
# USAGE EXAMPLE (CLI)
# ==========================================
if __name__ == "__main__":
    sample_payload = {
        "user_context": {
            "region_id": "Satara",
            "season": "Kharif"
        },
        "soil_data": {
            "nitrogen": 90,
            "phosphorus": 42,
            "potassium": 43,
            "ph": 6.5
        },
        # "weather_data": MISSING TEST
        "request_metadata": {
            "max_results": 3
        }
    }
    
    print("--- INFERENCE REQUEST (Missing Weather) ---")
    print(json.dumps(sample_payload, indent=2))
    
    result = predict(sample_payload)
    
    print("\n--- INFERENCE RESPONSE ---")
    print(json.dumps(result, indent=2))