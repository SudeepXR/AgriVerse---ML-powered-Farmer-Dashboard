# Step 2 Validation Report

**Date:** 2026-01-20
**Status:** APPROVED WITH CONDITIONS
**Reviewer:** ML Systems Engineer

---

## 1. Data Inventory

| Filename | Rows | Granularity | Key Columns |
| :--- | :--- | :--- | :--- |
| `CropDataset-Enhanced.csv` | 731 | District | Region, Crop (list), N/P/K distributions |
| `Crop_recommendation.csv` | 2,201 | Synthetic / Point | N, P, K, pH, Rainfall, Label |
| `crop_production.csv` | 246,092 | District-Season | State, District, Season, Crop, Production |
| `crop_yield.csv` | 1,000,001 | Broad Region | Region (North/South...), Yield |
| `Custom_Crops_yield...csv` | 50,766 | District | N_req, P_req, K_req, Yield |
| `India Ag...Production.csv` | 345,408 | District-Season | *Redundant with crop_production.csv* |

---

## 2. Validation & Role Assignment

### A. `CropDataset-Enhanced.csv`
*   **Role:** **Hard Feasibility Filter** (Primary)
*   **PRD Alignment:** **YES**. Directly supports the "Region-based" input requirement. Allows the system to function even if the user knows nothing about their soil.
*   **Status:** ✅ **VALID**

### B. `Crop_recommendation.csv`
*   **Role:** **Similarity Scoring Engine** (Auxiliary)
*   **PRD Alignment:** **CONDITIONAL**.
    *   *Risk:* Requires precise N/P/K inputs which users likely lack.
    *   *Mitigation:* Must be paired with `CropDataset-Enhanced.csv` for imputation.
    *   *Constraint:* Output must be treated as a "similarity score" (0-1), not a probability of success.
*   **Status:** ⚠️ **CONDITIONALLY VALID** (Strictly for ranking, not prediction).

### C. `crop_production.csv`
*   **Role:** **Seasonality & Historical Verification**
*   **PRD Alignment:** **YES**. Essential for filtering crops by "Season" (e.g., ensuring Winter crops aren't suggested in Summer).
*   **Status:** ✅ **VALID**

### D. `crop_yield.csv`
*   **Role:** **NONE**
*   **Reason:** Targets *Yield Prediction*, which is explicitly a **Non-Goal** in the PRD. The "Region" column (North/South) is too coarse for district-level decision support.
*   **Status:** ❌ **INVALID** (Do not use).

### E. `Custom_Crops_yield_Historical_Dataset.csv`
*   **Role:** **Reference / Documentation**
*   **Reason:** Contains useful metadata about nutrient *requirements* (`N_req`), which can support the "Reasoning" / "Explainability" text (FR-3). Not to be used for the core ranking model.
*   **Status:** ⚠️ **CONDITIONALLY VALID** (Metadata lookup only).

### F. `India Agriculture Crop Production.csv`
*   **Role:** **NONE**
*   **Reason:** Redundant duplicate of `crop_production.csv`.
*   **Status:** ❌ **INVALID** (Exclude to prevent confusion).

---

## 3. Final Summary & Sign-Off

**Approved for Pipeline:**
1.  `CropDataset-Enhanced.csv` (The Map)
2.  `Crop_recommendation.csv` (The Compass)
3.  `crop_production.csv` (The Calendar)

**Excluded:**
*   `crop_yield.csv` (Out of scope)
*   `India Agriculture Crop Production.csv` (Duplicate)

**Risks & Constraints:**
*   **Imputation Risk:** The system relies heavily on `CropDataset-Enhanced.csv` to fill in missing soil data for `Crop_recommendation.csv`. If a district is missing from the enhanced dataset, the fallback strategy must be robust (e.g., State-level average).
*   **False Precision:** The ML model (`Crop_recommendation`) trains on exact float values. The UI/API layer **MUST NOT** expose these inputs as mandatory, or users will enter random numbers.

**Conclusion:**
Step 2 is **COMPLETE** and **VALIDATED**. The data layer is sufficient to build the auxiliary decision-support system described in the PRD.
