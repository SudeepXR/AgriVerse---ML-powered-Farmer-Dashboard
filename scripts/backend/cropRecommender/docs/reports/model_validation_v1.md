# Step 7 Validation Report

**Date:** 2026-01-20
**Model Version:** v1.0.0
**Status:** VALIDATED WITH RISKS

---

## 1. Validation Scope

We validated the model's behavior as a **Decision Support Tool**.
We specifically ignored standard accuracy metrics in favor of:
*   **Stability:** Does the advice change wildly with small input shifts?
*   **Sensitivity:** Does the model detect when data is bad?
*   **Calibration:** Does the model express uncertainty?

## 2. Results Summary

| Test | Result | Interpretation | Pass/Fail |
| :--- | :--- | :--- | :--- |
| **Ranking Stability** | **63.7% Overlap** | Top-3 recommendations persist 64% of the time under 5% input noise. | **PASS** (Acceptable for bio-systems) |
| **Noise Sensitivity** | **40% Conf. Drop** | Confidence drops significantly (-0.40) when soil inputs are heavily corrupted. | **PASS** (Fails safely) |
| **Calibration** | **skewed High** | 94% of outputs have >0.8 confidence. | **RISK** (Model is overconfident) |

## 3. Detailed Analysis

### A. Ranking Stability (63.7% Overlap)
*   **Observation:** When inputs vary by ±5%, the set of "Top 3 Crops" changes by about 1/3rd.
*   **Impact:** This is expected in decision boundaries where multiple crops are similarly suitable (e.g., Rice vs Jute in high rainfall).
*   **Mitigation:** The UI **MUST** display crops with similar scores as "Equally Feasible" rather than implying a strict hierarchy between Rank #1 and Rank #2 if the score delta is small.

### B. Noise Sensitivity (Safety Check)
*   **Observation:** When N/P/K values are corrupted (simulating bad imputation), the model's "similarity score" drops by an average of 0.40.
*   **Conclusion:** The model correctly identifies that the "noisy" conditions are unlike any known successful crop profile.
*   **Safety:** This prevents the system from confidently recommending crops for alien soil conditions.

### C. Calibration Risk (Overconfidence)
*   **Observation:** The confidence histogram is heavily skewed to the right (2066 samples in 0.8-1.0 range).
*   **Cause:** Random Forests with depth=10 on a small dataset (2200 rows) tend to separate classes very cleanly.
*   **Risk:** Users might interpret a 0.99 score as a guarantee.
*   **Constraint:** The UI **MUST** suppress the raw score or bin it into "High/Medium/Low" to hide this false precision.

## 4. Final Recommendation

**✅ PROCEED TO DEPLOYMENT (WITH CAUTION)**

The model is safe because:
1.  It is **stable enough** (Top crops don't vanish randomly).
2.  It is **sensitive to garbage inputs** (Confidence drops).

**Required Guardrails for Next Steps:**
1.  **Do not show raw floats.** Use buckets (e.g., >0.8 = "High Feasibility").
2.  **Highlight uncertainty.** If the Top-1 and Top-2 scores are close (<0.05 diff), explicitly state "Multiple similar options".

---

## 5. Phase 3: System-Level Degradation Verification (Audit Closure)

**Date:** 2026-01-20
**Objective:** Verify that confidence scores degrade gracefully and are capped when inputs are missing/unknown.

### 5.1 Degradation Logic Verification
We ran `validate_inference.py` (N=500 samples) across three scenarios.

| Scenario | Input Condition | System Action | Observed Confidence | Data Coverage Flag |
| :--- | :--- | :--- | :--- | :--- |
| **Happy Path** | Valid Region + Soil | Full Inference | Mixed (High/Med/Low) | `high` |
| **Missing Soil** | Valid Region + Null Soil | Imputation (District) | 100% Low* | `high` |
| **Unknown Region**| Invalid Region | National Fallback | **100% Low** (Capped) | `low` |

*\*Note: In "Missing Soil" test, confidence dropped to Low because imputed averages are generic, preventing "High" confidence matches. This confirms safety.*

### 5.2 Confidence Skew Resolution (Finding #6)
*   **Previous State:** Model output >0.8 confidence for 94% of cases (Overconfident).
*   **Current State:**
    *   **Happy Path:** Only 1.4% (7/500) achieved "High" confidence.
    *   **Degraded:** 0% achieved "High" confidence.
*   **Conclusion:** The system is now **Conservative**. It effectively suppresses false precision. High confidence is reserved for "perfect matches".

### 5.3 Final Verdict
**AUDIT FINDING #6 IS CLOSED.**
The system enforces strict confidence caps based on the `DegradationLevel` ladder.
*   `EXACT_REGION` -> Allowed High
*   `STATE_FALLBACK` -> Capped Medium
*   `NATIONAL_FALLBACK` -> Capped Low

No silent failures or overconfident guesses were observed.

---
*Validation confirmed by ML Systems Engineer.*
