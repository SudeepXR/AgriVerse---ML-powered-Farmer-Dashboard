# Data Manifest

**Version:** 2.0.0
**Last Updated:** 2026-01-21

This document serves as the authoritative source of truth for all datasets approved for use in the Crop Recommender ML Pipeline.

## 1. Primary Datasets

| Dataset Name | Filename | Role | Usage | Validation Status |
| :--- | :--- | :--- | :--- | :--- |
| **Crop Recommendation** | `Crop_recommendation.csv` | Training Data | Used to train the Shallow Random Forest model. Provides features (N, P, K, Temp, Hum, pH, Rain) and Labels (Crop). | APPROVED |
| **Regional Profiles** | `CropDataset-Enhanced.csv` | Reference Data | Source for generating `regional_profiles.csv`. Used for regional feasibility filtering and soil imputation. | APPROVED |
| **Production History** | `crop_production.csv` | Reference Data | Source for generating `seasonality_log.csv`. Used for seasonal feasibility filtering. | APPROVED |
| **Weather Historical** | `Custom_Crops_yield_Historical_Dataset.csv` | Reference Data | Source for district-level climate averages (Temperature, Humidity, Rainfall) in `regional_profiles.csv`. | APPROVED |

## 2. Derived Artifacts

| Artifact Name | Source | Purpose |
| :--- | :--- | :--- |
| `ml_training.csv` | `Crop_recommendation.csv` | Cleaned training subset used by `train_model.py`. |
| `regional_profiles.csv` | `CropDataset-Enhanced.csv` + `Custom_Crops_yield_Historical_Dataset.csv` | Lookup table for District -> {Avg Soil, Avg Weather, Allowed Crops}. Used in Phase 1 Filter, Soil/Weather Imputation. |
| `seasonality_log.csv` | `crop_production.csv` | Lookup table for (District, Season) -> {Allowed Crops}. Used in Phase 2 Filter. |

## 3. Usage Rules

1.  **Imputation**: When user soil data is missing, values MUST be sourced from `regional_profiles.csv`. Static constants are FORBIDDEN.
2.  **Filtering**: 
    *   **Phase 1**: Candidates must exist in `regional_profiles.csv` for the target district.
    *   **Phase 2**: Candidates must exist in `seasonality_log.csv` for the target district AND season.
3.  **Weather Imputation**: Weather data is derived from `regional_profiles.csv` using historical district-level averages. Users do NOT provide weather inputs.

## 4. Updates & Versioning

*   New datasets require a full audit and entry update in this manifest.
*   Schema changes to any CSV must be reflected in `data/schemas/`.

## 5. Reference Scope & Fallback Policy

The system employs a controlled degradation strategy to handle missing or unmapped regions. This section maps the Degradation Ladder to specific data artifacts.

### Level 1: Exact Region (High Precision)
*   **Trigger:** `region_id` exists in `regional_profiles.csv`.
*   **Data Source:** 
    *   **Soil Imputation:** Specific row in `regional_profiles.csv`.
    *   **Feasibility Filter:** Specific row in `regional_profiles.csv` (Crops list).
    *   **Seasonality:** Specific (District, Season) row in `seasonality_log.csv`.
*   **Loss:** None. Ideal state.

### Level 2: State Fallback (Medium Precision)
*   **Trigger:** District unknown, but State is valid.
*   **Data Source:**
    *   **Soil Imputation:** Aggregated average of all districts in that State from `regional_profiles.csv`.
    *   **Feasibility Filter:** Union of all crops grown in that State from `regional_profiles.csv`.
*   **Loss:** Micro-climate nuances. District-specific soil variations are smoothed out.
*   **Safety:** Confidence capped at **Medium**.

### Level 3: National Fallback (Low Precision)
*   **Trigger:** Region completely unknown.
*   **Data Source:**
    *   **Soil Imputation:** Global average of the entire `regional_profiles.csv` dataset.
    *   **Feasibility Filter:** All crops in the system (National scope).
*   **Loss:** All geographic context. Recommendations are based purely on Weather/Soil match.
*   **Safety:** Confidence capped at **Low**. Metadata explicitly flags coverage as "low".
