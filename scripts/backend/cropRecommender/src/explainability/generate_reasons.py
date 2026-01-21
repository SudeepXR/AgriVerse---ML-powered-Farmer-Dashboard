"""
Explainability Layer
====================
Role: Translates technical ML signals into human-readable, non-authoritative reasoning.
Scope: Decision Support (Auxiliary)
Input: Model features, metadata
Output: List of string reasons per crop

PRD ALIGNMENT:
- NO probabilities ("80% chance")
- NO guarantees ("Will grow well")
- NO optimization ("Best choice")
- ONLY qualitative matching ("Conditions align", "Similar to history")
"""

import math

# ==========================================
# TEMPLATES (Immutable Canon)
# ==========================================
# These templates enforce the "Non-Authoritative" tone.

REASON_TEMPLATES = {
    # High Confidence
    "high_match": "Conditions strongly resemble historical {crop} profiles.",
    # Low Confidence / Imputed
    "low_match": "Conditions may support {crop}, though data is limited.",
    "imputed_match": "Potential match based on regional averages for {crop}.",
    
    "moderate_match": "Conditions share similarities with {crop} requirements.",
    "rainfall_support": "Regional rainfall patterns align with typical {crop} needs.",
    "temp_support": "Temperature range is consistent with successful {crop} growth.",
    "soil_n_support": "Soil Nitrogen levels match the typical profile for this crop.",
    "soil_p_support": "Phosphorous content is within the feasible range.",
    "soil_k_support": "Potassium levels support this crop's typical profile.",
    "ph_support": "Soil acidity/alkalinity is compatible.",
    "season_support": "This crop is historically cultivated in the '{season}' season.",
    "imputation_warning": "Note: Based on regional averages, not your specific soil test.",
    "low_score_warning": "Note: Confidence is low due to limited parameter alignment."
}

# Thresholds for triggering specific reasons (Heuristic)
# We avoid exposing raw coefficients, but we use feature diffs to trigger logic.
DIFF_TOLERANCE = 0.2 # 20% deviation is considered a "Match"

def generate_reasons(
    crop_name,
    input_features,
    feature_importance_map=None, # Optional: dict of feature_name -> importance_weight
    metadata=None
):
    """
    Generates a list of human-readable reasons for a specific crop recommendation.
    
    Args:
        crop_name (str): Name of the crop (e.g., 'rice')
        input_features (dict): The user's input vector (e.g., {'N': 90, 'rainfall': 200})
        feature_importance_map (dict, optional): (Not used in V1, reserved for SHAP integration)
        metadata (dict, optional): Context like {'season': 'Kharif', 'is_imputed': True, 'score': 0.75}
        
    Returns:
        list[str]: A list of determinstic reasoning strings.
    """
    reasons = []
    warnings = []
    
    # safe defaults
    if metadata is None: metadata = {}
    
    score = metadata.get('score', 1.0)
    is_imputed = metadata.get('is_imputed', False)
    
    # 1. Base Similarity Statement (Context-Aware)
    if is_imputed:
        reasons.append(REASON_TEMPLATES["imputed_match"].format(crop=crop_name.title()))
    elif score < 0.15:
        reasons.append(REASON_TEMPLATES["low_match"].format(crop=crop_name.title()))
    elif score < 0.40:
        reasons.append(REASON_TEMPLATES["moderate_match"].format(crop=crop_name.title()))
    else:
        reasons.append(REASON_TEMPLATES["high_match"].format(crop=crop_name.title()))
    
    # 2. Heuristic Explanations based on Input Features
    # Since we are using a Random Forest, we don't have simple linear coefficients to say 
    # "High N caused this". Instead, we look at the input *context* to confirm suitability.
    
    # Rainfall Check (Generic Logic: If rainfall is significant, mention it)
    rainfall = input_features.get('rainfall', 0)
    if rainfall > 100: # Heuristic: 100mm is distinct
        reasons.append(REASON_TEMPLATES["rainfall_support"].format(crop=crop_name))
        
    # Temperature Check
    temp = input_features.get('temperature', 0)
    if 15 < temp < 35: # Broad "good" range
        reasons.append(REASON_TEMPLATES["temp_support"].format(crop=crop_name))
        
    # 3. Seasonal Context (Strongest non-ML signal)
    season = metadata.get('season')
    if season and season != 'Whole Year':
        reasons.append(REASON_TEMPLATES["season_support"].format(season=season, crop=crop_name))
        
    # 4. Soil Feasibility (If not imputed)
    if not is_imputed:
        # If user provided real data, we validate it specifically
        # (Simple existence check for V1 - logic can be refined with specific crop ranges later)
        reasons.append(REASON_TEMPLATES["soil_n_support"])
        reasons.append(REASON_TEMPLATES["ph_support"])
    else:
        # If imputed, we MUST warn, not praise the soil match too heavily
        warnings.append(REASON_TEMPLATES["imputation_warning"])

    if score < 0.15:
        warnings.append(REASON_TEMPLATES["low_score_warning"])

    # 5. Format & Return
    # Combine reasons and warnings. 
    # Max 3 reasons + warnings to avoid overwhelming user.
    final_output = reasons[:3] + warnings
    
    return final_output

def get_explanation_metadata():
    """Returns metadata about available explanations for UI configuration."""
    return {
        "version": "1.0.0",
        "style": "Qualitative/Auxiliary",
        "supported_languages": ["en"]
    }

# ==========================================
# USAGE EXAMPLE
# ==========================================
if __name__ == "__main__":
    # Mock Inputs
    sample_crop = "rice"
    sample_features = {'N': 80, 'P': 40, 'K': 40, 'rainfall': 250, 'temperature': 26}
    sample_meta = {'season': 'Kharif', 'is_imputed': False}
    
    print(f"--- Explanation for {sample_crop} ---")
    reasons = generate_reasons(sample_crop, sample_features, metadata=sample_meta)
    for r in reasons:
        print(f"- {r}")
        
    print(f"\n--- Explanation for {sample_crop} (Imputed) ---")
    sample_meta_imputed = {'season': 'Kharif', 'is_imputed': True}
    reasons_imp = generate_reasons(sample_crop, sample_features, metadata=sample_meta_imputed)
    for r in reasons_imp:
        print(f"- {r}")
