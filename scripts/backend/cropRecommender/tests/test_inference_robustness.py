import sys
import os
import pytest
import json
from unittest.mock import patch

# Adjust path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.inference.predict import predict
from src.inference.degradation import DegradationLevel

# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def valid_payload():
    return {
        "user_context": {
            "region_id": "Satara, Maharashtra", # Must be a valid region for imputation tests
            "season": "Kharif"
        },
        "soil_data": {
            "nitrogen": 50,
            "phosphorus": 50,
            "potassium": 50,
            "ph": 6.5
        },
        "request_metadata": {
            "max_results": 3
        }
    }

# ==========================================
# 1. MISSING INPUTS TESTS
# ==========================================

def test_missing_user_context_fails(valid_payload):
    """Test that missing required context returns a clear error."""
    payload = valid_payload.copy()
    del payload['user_context']
    
    response = predict(payload)
    
    assert response['status'] == 'error'
    assert "Missing 'user_context'" in response['message']

def test_missing_region_fails(valid_payload):
    """Test that missing region_id returns a clear error."""
    payload = valid_payload.copy()
    payload['user_context'] = {"season": "Kharif"} # No region_id
    
    response = predict(payload)
    
    assert response['status'] == 'error'
    assert "Missing 'region_id'" in response['message']

def test_missing_soil_data_imputes_safely(valid_payload):
    """Test that missing soil data triggers imputation and warnings."""
    payload = valid_payload.copy()
    del payload['soil_data']
    
    response = predict(payload)
    
    assert response['status'] == 'success'
    assert response['meta']['used_imputed_soil_data'] is True
    
    # Check that imputation warning exists in explanations/warnings
    rec = response['recommendations'][0]
    has_warning = any("regional averages" in r for r in rec['reasoning']) or any("regional averages" in w for w in rec['warnings'])
    assert has_warning, "Imputation warning missing from reasoning/warnings"

# ==========================================
# 2. EXTREME VALUES TESTS (STABILITY)
# ==========================================

def test_extreme_soil_values_rejected(valid_payload):
    """Test that physically extreme inputs are REJECTED (Strict Validation)."""
    payload = valid_payload.copy()
    payload['soil_data'] = {
        "nitrogen": 5000,   # Impossible High
        "phosphorus": -100, # Impossible Low
        "potassium": 0,
        "ph": 14.0          # Extreme Basic (Allowed but edge)
    }
    
    response = predict(payload)
    
    assert response['status'] == 'error'
    assert "out of range" in response['message'].lower()

# ==========================================
# 3. MODEL UNAVAILABLE TESTS (FAIL SAFE)
# ==========================================

@patch('src.inference.predict.load_latest_model_and_meta')
def test_model_loading_failure_handled(mock_loader, valid_payload):
    """Test that internal model errors result in a clean error response."""
    # Simulate a missing artifact or corrupt file
    mock_loader.side_effect = RuntimeError("Model artifacts directory missing.")
    
    response = predict(valid_payload)
    
    assert response['status'] == 'error'
    # Message should be user-safe but descriptive enough
    assert "Model artifacts directory missing" in response['message']
    # Ensure no raw stack trace leaked into the 'status' field
    assert len(response.keys()) <= 3 # status, message, maybe model_version

# ==========================================
# 4. EXPLANATION COMPLIANCE TESTS
# ==========================================

def test_explanations_are_compliant(valid_payload):
    """Test that explanations avoid forbidden prescriptive language."""
    response = predict(valid_payload)
    
    assert response['status'] == 'success'
    recs = response['recommendations']
    
    forbidden_terms = ["guaranteed", "best crop", "100%", "profit", "prediction"]
    
    for rec in recs:
        reasons = rec['reasoning']
        assert isinstance(reasons, list)
        assert len(reasons) > 0
        
        full_text = " ".join(reasons).lower()
        for term in forbidden_terms:
            assert term not in full_text, f"Found forbidden term '{term}' in explanation."

def test_explanation_determinism(valid_payload):
    """Test that identical inputs produce identical explanation text."""
    resp1 = predict(valid_payload)
    resp2 = predict(valid_payload)
    
    rec1 = resp1['recommendations'][0]
    rec2 = resp2['recommendations'][0]
    
    assert rec1['crop_name'] == rec2['crop_name']
    assert rec1['reasoning'] == rec2['reasoning']

# ==========================================
# 5. SCHEMA COMPLIANCE (IMPLICIT)
# ==========================================

def test_valid_payload_returns_valid_schema(valid_payload):
    """
    Since predict.py uses internal schema validation, 
    a success response implies schema compliance.
    We just verify the structure explicitly here.
    """
    response = predict(valid_payload)
    
    assert response['status'] == 'success'
    assert 'meta' in response
    assert 'disclaimer' in response['meta']
    assert 'recommendations' in response
    
    top_rec = response['recommendations'][0]
    assert 'rank' in top_rec
    assert 'feasibility_score' in top_rec
    assert 'confidence_level' in top_rec

# ==========================================
# 6. UNKNOWN REGION TEST (Fail-Soft)
# ==========================================

def test_unknown_region_falls_back_safely(valid_payload):
    """
    Test that an unknown region triggers National Fallback (Low Confidence)
    instead of crashing or returning empty results blindly.
    """
    payload = valid_payload.copy()
    payload['user_context']['region_id'] = "Unknown_Region_XYZ"
    
    response = predict(payload)
    
    assert response['status'] == 'success'
    assert response['meta']['data_coverage'] == 'low'
    
    # Verify warnings exist about the unknown region
    has_warning = False
    for rec in response['recommendations']:
        for w in rec['warnings']:
            if "unknown" in w.lower() or "national" in w.lower():
                has_warning = True
                break
    assert has_warning, "Expected warning about Unknown Region usage."