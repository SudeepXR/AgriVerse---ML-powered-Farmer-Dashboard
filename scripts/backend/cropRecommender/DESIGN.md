# System Design & Canon

**Status:** ACTIVE / DEPLOYED
**Version:** 2.2.0
**Scope:** Architecture, ML Semantics, API Contract, Degradation Strategy, and Training Validation.

---

## 1. Core Philosophy

This service is an **Auxiliary Decision-Support Tool**, not an automated agronomist.

*   **Role:** It provides probabilistic signals ("Feasibility Scores") to support human judgment.
*   **Non-Goal:** It does **NOT** predict yield, profit, or success probability.
*   **Transparency:** Every output must include reasoning, confidence levels, and warnings.
*   **Fail-Soft:** The system prefers a "low-confidence, broad recommendation" over a hard crash or silent guess.

---

## 2. ML Problem Definition

The Machine Learning component is defined as a **Multi-Class Similarity Ranker**.

*   **Input:** Environmental vector (Soil N/P/K/pH + Weather Temp/Hum/Rain).
*   **Output:** A ranked list of crop candidates sorted by their alignment with historical conditions.
*   **Score Semantics:**
    *   The score $S \in [0.0, 1.0]$ represents **Similarity** to the centroid of historical profiles.
    *   $S=0.9$ means "Conditions are very similar to where this crop typically grows."
    *   $S \neq$ Probability of success.
    *   $S \neq$ Predicted Yield.

## 2.1 Training & Validation
To ensure the "Relative Feasibility" score is reliable, the model training pipeline enforces:
*   **Split Validation:** 80% Training / 20% Testing split.
*   **Metric Logging:** Accuracy and F1-Macro scores are computed on the held-out test set and logged to the model metadata.
*   **No Overfitting:** Models without validation metrics are considered "Unverified".

---

## 3. System Architecture: The Hybrid Pipeline

The inference logic follows a strict 4-phase execution order to prevent hallucinations (e.g., suggesting Rice in a desert due to soil match alone).

**Configuration Source of Truth:** `src/config.py` centralizes all thresholds, paths, and feature definitions to ensure parity between Training and Inference.

### Phase 1: Regional Feasibility Filter (Non-ML)
*   **Input:** `region_id`
*   **Action:** Look up the "Physical Possibility List" for the district/state from `regional_profiles.csv`.
*   **Constraint:** If a crop is not in this list, it is **REJECTED** regardless of ML score.

### Phase 2: Contextual Refinement (Heuristic)
*   **Input:** Candidate List from Phase 1, `season`
*   **Action:** Filter crops incompatible with the current season (if season is provided).

### Phase 3: Similarity Scoring (ML Model)
*   **Input:** Filtered Candidates, Soil/Weather Data.
*   **Action:** Score each candidate using the Random Forest classifier.
*   **Data Source:**
    *   **Soil:** User-provided OR Imputed from `region_id` using district averages.
    *   **Weather:** ALWAYS imputed from `region_id` using historical district climate averages (User input forbidden).

### Phase 4: Post-Processing
*   **Action:**
    *   Apply Confidence Caps based on Degradation Level.
    *   Generate Explainability strings.
    *   Append warnings.

---

## 4. Fail-Soft & Degradation Strategy

The system must handle incomplete data gracefully.

| Input Scenario | Degradation Level | System Behavior | Confidence Cap |
| :--- | :--- | :--- | :--- |
| **Valid Region + Known District** | `EXACT_REGION` | Full precision inference. | **High** |
| **Valid Region + Unknown District** | `STATE_FALLBACK` | Use State-level averages. | **Medium** |
| **Unknown Region** | `NATIONAL_FALLBACK` | Use National averages. | **Low** |
| **Missing Soil Data** | N/A | Impute from Region. | No Cap* |

*Note: Imputed soil naturally tends to produce lower similarity scores, self-regulating the confidence.*

**Validation Rules:**
*   **Missing `region_id`** → **HTTP 400 (Fail Fast)**.
*   **Partial `soil_data`** → **HTTP 400 (Fail Fast)**.
*   **Missing `soil_data`** → **Proceed (Fail Soft)** with imputation + metadata flag.

---

## 5. API Contract

### Request (`POST /predict`)
```json
{
  "user_context": {
    "region_id": "Satara, Maharashtra",  // REQUIRED
    "season": "Kharif"                   // OPTIONAL
  },
  "soil_data": {
    "nitrogen": 90,
    "phosphorus": 42,
    "potassium": 43,
    "ph": 6.5
  },
  "request_metadata": {
    "max_results": 5
  }
}
```

### Response
```json
{
  "status": "success",
  "meta": {
    "data_coverage": "high",             // high/medium/low
    "used_imputed_soil_data": false,
    "disclaimer": "Auxiliary insight only..."
  },
  "recommendations": [
    {
      "crop_name": "Rice",
      "feasibility_score": 0.85,
      "confidence_level": "High",
      "reasoning": ["Matches historical rainfall..."],
      "warnings": []
    }
  ]
}
```

---

## 6. Data Roles

*   **`regional_profiles.csv`**: Source of truth for **Phase 1 (Filtering)**, **Soil Imputation**, and **Weather Imputation**. Derived from `CropDataset-Enhanced.csv` (soil) and `Custom_Crops_yield_Historical_Dataset.csv` (weather).
*   **`Crop_recommendation.csv`**: The training dataset for **Phase 3 (Scoring)**.
*   **`ml_training.csv`**: Processed training set.

---
