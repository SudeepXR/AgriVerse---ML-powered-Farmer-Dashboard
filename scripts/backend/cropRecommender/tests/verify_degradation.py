import sys
import os
import json
import pytest

# Adjust path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.inference.predict import predict

def test_happy_path():
    """Scenario 1: Happy Path (Satara, Kharif, Soil Data Provided)"""
    payload = {
        "user_context": {"region_id": "Satara, Maharashtra", "season": "Kharif"},
        "soil_data": {"nitrogen": 90, "phosphorus": 42, "potassium": 43, "ph": 6.5},
        "weather_data": {"temperature": 25.0, "humidity": 80.0, "rainfall": 120.0}
    }
    result = predict(payload)
    print("\n--- HAPPY PATH ---")
    print(json.dumps(result, indent=2))
    
    assert result['status'] == "success"
    assert result['meta']['data_coverage'] == "high" # Or medium depending on degradation logic
    assert not result['meta']['used_imputed_soil_data']
    assert len(result['recommendations']) > 0

def test_unknown_region_fallback():
    """Scenario 2: Unknown Region -> National Fallback"""
    payload = {
        "user_context": {"region_id": "Atlantis", "season": "Kharif"},
        "weather_data": {"temperature": 25.0, "humidity": 80.0, "rainfall": 120.0}
    }
    result = predict(payload)
    print("\n--- UNKNOWN REGION ---")
    print(json.dumps(result, indent=2))
    
    assert result['status'] == "success"
    assert result['meta']['data_coverage'] == "low"
    assert "national" in result['meta']['disclaimer'].lower()
    assert len(result['recommendations']) > 0
    # Check for specific warning
    has_warning = any("Region 'Atlantis' unknown" in w for r in result['recommendations'] for w in r.get('warnings', []))
    if not has_warning:
         # Might be in disclaimer
         has_warning = "Region 'Atlantis' unknown" in result['meta']['disclaimer']
    assert has_warning

def test_unknown_season_fallback():
    """Scenario 3: Unknown Season -> Seasonal Filter Skipped"""
    payload = {
        "user_context": {"region_id": "Satara, Maharashtra", "season": "Martian Winter"},
        "soil_data": {"nitrogen": 90, "phosphorus": 42, "potassium": 43, "ph": 6.5},
        "weather_data": {"temperature": 25.0, "humidity": 80.0, "rainfall": 120.0}
    }
    result = predict(payload)
    print("\n--- UNKNOWN SEASON ---")
    print(json.dumps(result, indent=2))
    
    assert result['status'] == "success"
    assert len(result['recommendations']) > 0
    
    # Check for warning in disclaimer or items
    disclaimer = result['meta']['disclaimer']
    warnings = [w for r in result['recommendations'] for w in r.get('warnings', [])]
    combined_text = disclaimer + " ".join(warnings)
    
    # Accept either explicit missing data warning OR relaxation warning
    success_indicators = [
        "Seasonal data missing",
        "Skipping seasonal filter",
        "No crops matched seasonal criteria",
        "Showing regionally feasible options"
    ]
    
    assert any(indicator in combined_text for indicator in success_indicators), \
        f"Expected degradation warning not found in: {combined_text}"

def test_strict_filter_empty_result_relaxation():
    """Scenario 4: Valid Inputs but Empty Intersection -> Relaxation"""
    # Using Satara + Rabi (which previously returned empty due to strict filters)
    payload = {
        "user_context": {"region_id": "Satara, Maharashtra", "season": "Rabi"},
        "weather_data": {"temperature": 20.0, "humidity": 50.0, "rainfall": 10.0}
        # Missing soil data -> Imputation
    }
    result = predict(payload)
    print("\n--- EMPTY RESULT RELAXATION ---")
    print(json.dumps(result, indent=2))
    
    assert result['status'] == "success"
    assert len(result['recommendations']) > 0
    
    # Must have warning about relaxation
    disclaimer = result['meta']['disclaimer']
    warnings = [w for r in result['recommendations'] for w in r.get('warnings', [])]
    combined_text = disclaimer + " ".join(warnings)
    
    # Either "No crops matched seasonal" or "No crops matched regional"
    assert "No crops matched" in combined_text

if __name__ == "__main__":
    try:
        test_happy_path()
        test_unknown_region_fallback()
        test_unknown_season_fallback()
        test_strict_filter_empty_result_relaxation()
        print("\n✅ ALL TESTS PASSED")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ SYSTEM ERROR: {e}")
        sys.exit(1)
