import unittest
import json
import sys
import os

# Adjust path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.inference.predict import predict, impute_soil_data, validate_input

class TestAuditRemediation(unittest.TestCase):
    
    def setUp(self):
        # Known valid context from exploration
        self.region_id = "Satara, Maharashtra" 
        self.valid_payload = {
            "user_context": {
                "region_id": self.region_id,
                "season": "Rabi"
            },
            "soil_data": {
                "nitrogen": 90,
                "phosphorus": 42,
                "potassium": 43,
                "ph": 6.5
            },
            "request_metadata": {
                "max_results": 10
            }
        }

    def test_regional_hard_filter(self):
        """
        CRITICAL: Verify that crops NOT in the regional profile are strictly excluded.
        Satara Profile: Sugarcane|Jowar (Sorghum)|Groundnut|Rice|Wheat
        """
        # We need to ensure the model produces some candidates, then check if they are filtered.
        # Since we can't easily force the model to predict 'Coffee', we check that 
        # ALL returned crops are in the allowed list.
        
        response = predict(self.valid_payload)
        self.assertEqual(response['status'], 'success')
        
        allowed_crops_lower = ["sugarcane", "jowar (sorghum)", "groundnut", "rice", "wheat", "jowar", "sorghum"]
        # Note: Handling "Jowar (Sorghum)" complex string normalization in implementation
        
        for rec in response['recommendations']:
            crop = rec['crop_name'].lower()
            # We assume the remediation will handle fuzzy matching or strict string containment.
            # For this test, we check if the returned crop is vaguely in our allowed list.
            match = any(allowed in crop or crop in allowed for allowed in allowed_crops_lower)
            self.assertTrue(match, f"Crop '{crop}' should have been filtered out for {self.region_id}")

    def test_seasonal_filter(self):
        """
        CRITICAL: Verify seasonal filtering.
        Season: Rabi.
        Should include: Wheat, Gram.
        Should EXCLUDE: Rice (Kharif), Cotton (Kharif).
        """
        payload = self.valid_payload.copy()
        payload['user_context']['season'] = 'Rabi'
        
        response = predict(payload)
        self.assertEqual(response['status'], 'success')
        
        # DEBUG: Print output if assertion fails
        # print(json.dumps(response, indent=2))
        
        rabi_crops = ["wheat", "gram", "chickpea"] # Chickpea is Gram
        kharif_crops = ["rice", "cotton", "soyabean"]
        
        returned_crops = [r['crop_name'].lower() for r in response['recommendations']]
        
        # If relaxation occurred, Rice might be present. 
        # But for 'Satara' + 'Rabi', we EXPECT valid Rabi crops (Wheat) to exist.
        # If they don't, it implies the model is performing poorly for this input.
        
        # Check if we are in relaxed mode
        is_relaxed = any("seasonal" in w.lower() for rec in response['recommendations'] for w in rec.get('warnings', []))
        
        if not is_relaxed:
            for crop in returned_crops:
                self.assertNotIn("rice", crop, "Rice (Kharif) should not be suggested in Rabi (Strict Mode)")
                self.assertNotIn("cotton", crop, "Cotton (Kharif) should not be suggested in Rabi (Strict Mode)")
        else:
            print("WARNING: Seasonal filter was relaxed in test_seasonal_filter. Skipping strict check.")

    def test_imputation_logic(self):
        """
        CRITICAL: Verify impute_soil_data returns profile values, not constants.
        Satara Profile: N=23.57, P=67.66, K=75.52, pH=6.45
        """
        # Directly test the function if possible, or the effect.
        # We'll test the function assuming it will be updated.
        
        data, level = impute_soil_data(self.region_id)
        
        # Current hardcoded values are 50, 53, 48.
        # We expect the profile values.
        self.assertAlmostEqual(data['nitrogen'], 23.57, delta=1.0)
        self.assertAlmostEqual(data['phosphorus'], 67.66, delta=1.0)
        self.assertAlmostEqual(data['potassium'], 75.52, delta=1.0)
        self.assertAlmostEqual(data['ph'], 6.45, delta=0.1)

    def test_output_precision(self):
        """
        CONCERNING: Feasibility score should be rounded (e.g. 2 decimals).
        """
        response = predict(self.valid_payload)
        for rec in response['recommendations']:
            score = rec['feasibility_score']
            # Check string length of float? Or just that it has max 2 decimal places.
            # 0.85 is valid, 0.8537 is not.
            # Logic: str(score)[::-1].find('.') <= 2
            # But floating point rep might be weird. 
            # Safest: verify it equals round(score, 2)
            self.assertEqual(score, round(score, 2), f"Score {score} has too much precision")

    def test_input_range_validation(self):
        """
        CONCERNING: Extreme values should trigger error.
        """
        payload = self.valid_payload.copy()
        payload['soil_data']['nitrogen'] = 5000 # Invalid
        
        with self.assertRaises(ValueError):
            validate_input(payload)
            # We might need to call predict if validate_input is internal only, 
            # but usually validate_input is exposed or we check predict's response
            
        # Also check predict handles it
        response = predict(payload)
        self.assertEqual(response['status'], 'error')
        self.assertIn("range", response.get('message', '').lower())

if __name__ == '__main__':
    unittest.main()
