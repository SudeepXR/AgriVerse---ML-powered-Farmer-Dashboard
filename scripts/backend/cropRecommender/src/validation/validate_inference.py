import os
import sys
import json
import csv
import numpy as np
from collections import Counter

# Adjust path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.inference.predict import predict
from src.inference.degradation import DegradationLevel

# ==========================================
# CONFIGURATION
# ==========================================

PROCESSED_DATA_PATH = "data/processed/ml_training.csv"
VALIDATION_OUTPUT_DIR = "src/validation/reports"
SAMPLE_SIZE = 500  # Validate a subset for speed, or len(data) for full

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def load_data(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def run_scenario(scenario_name, data, transformer_func):
    """
    Runs the inference pipeline on the data after applying a transformer function
    to simulate different scenarios (Happy Path, Missing Soil, Unknown Region).
    """
    print(f"\n--- Running Scenario: {scenario_name} ---")
    
    confidence_counts = Counter()
    degradation_counts = Counter()
    
    results = []
    
    # Process a sample
    sample_indices = np.random.choice(len(data), min(SAMPLE_SIZE, len(data)), replace=False)
    
    for i in sample_indices:
        row = data[i]
        
        # 1. Construct Payload via Transformer
        payload = transformer_func(row)
        
        # 2. Execute Pipeline
        response = predict(payload)
        
        # 3. Harvest Metrics
        if response['status'] == 'success':
            recs = response.get('recommendations', [])
            if recs:
                top_conf = recs[0]['confidence_level']
                confidence_counts[top_conf] += 1
            else:
                confidence_counts['No_Recs'] += 1
                
            coverage = response['meta']['data_coverage']
            degradation_counts[coverage] += 1
            
            results.append({
                "scenario": scenario_name,
                "coverage": coverage,
                "top_confidence": top_conf if recs else "None"
            })
            
    # Print Summary
    print(f"Confidence Distribution: {dict(confidence_counts)}")
    print(f"Coverage Distribution:   {dict(degradation_counts)}")
    
    return confidence_counts, degradation_counts

# ==========================================
# SCENARIO TRANSFORMERS
# ==========================================

def transform_happy_path(row):
    """Scenario 1: Ideal inputs (Satara is our testbed region)"""
    return {
        "user_context": {
            "region_id": "Satara, Maharashtra",
            "season": "Kharif" # Arbitrary valid season
        },
        "soil_data": {
            "nitrogen": float(row['N']),
            "phosphorus": float(row['P']),
            "potassium": float(row['K']),
            "ph": float(row['ph'])
        }
        # weather_data REMOVED (Simulate Public API)
    }

def transform_missing_soil(row):
    """Scenario 2: Missing Soil Data (Imputation Triggered)"""
    # Should result in 'state_fallback' or 'exact_region' imputation depending on data availability
    # Satara exists, so it should be exact_region or state_fallback logic
    return {
        "user_context": {
            "region_id": "Satara, Maharashtra",
            "season": "Kharif"
        }
        # No soil_data key
        # weather_data REMOVED (Simulate Public API)
    }

def transform_unknown_region(row):
    """Scenario 3: Unknown Region (National Fallback)"""
    return {
        "user_context": {
            "region_id": "Atlantis", # Unknown
            "season": "Kharif"
        }
        # weather_data REMOVED (Simulate Public API)
    }

# ==========================================
# MAIN
# ==========================================

def run_validation():
    if not os.path.exists(VALIDATION_OUTPUT_DIR):
        os.makedirs(VALIDATION_OUTPUT_DIR)
        
    raw_data = load_data(PROCESSED_DATA_PATH)
    
    report = {
        "scenarios": {}
    }
    
    # 1. Happy Path
    conf, cov = run_scenario("Happy Path", raw_data, transform_happy_path)
    report["scenarios"]["happy_path"] = {"confidence": dict(conf), "coverage": dict(cov)}
    
    # 2. Missing Soil
    conf, cov = run_scenario("Missing Soil", raw_data, transform_missing_soil)
    report["scenarios"]["missing_soil"] = {"confidence": dict(conf), "coverage": dict(cov)}
    
    # 3. Unknown Region
    conf, cov = run_scenario("Unknown Region", raw_data, transform_unknown_region)
    report["scenarios"]["unknown_region"] = {"confidence": dict(conf), "coverage": dict(cov)}
    
    # Save Report
    out_path = os.path.join(VALIDATION_OUTPUT_DIR, "inference_validation_results.json")
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nInference Validation Complete. Results saved to {out_path}")

if __name__ == "__main__":
    np.random.seed(42)
    run_validation()
