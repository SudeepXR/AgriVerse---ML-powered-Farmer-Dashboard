# AUDIT REPORT: Crop Recommender Inference Service

**Date:** 21 January 2026
**Auditor:** Gemini CLI
**Version:** 1.0.0
**Scope:** `src/`, `tests/`, `data/`, `models/`

---

## 1. Executive Summary

**Verdict: FAIL**

The system implementation diverges critically from the documented API contract in a way that creates a permanent **Denial of Service (Quality)** for compliant clients. While the core ML and Fail-Soft logic are implemented, the handling of `weather_data` violates the Canon. The API strictly forbids users from providing weather data, yet the internal logic *requires* it to avoid degrading to "National Fallback" (Low Confidence).

Furthermore, the test suite masks this failure by injecting undocumented `weather_data` fields into test payloads, creating a false "PASS" state. If deployed as is, **100% of valid user requests will return Low Confidence results**, rendering the "Auxiliary Intelligence" feature useless.

---

## 2. Findings by Category

### A. System Architecture & Flow (CRITICAL)

*   **Issue:** **Implicit Degradation Trap (Weather Data)**
*   **Location:** `src/inference/predict.py` (Lines 207-217, 303-305)
*   **Description:** The `predict.py` logic forces `weather_imputation_level = NATIONAL_FALLBACK` if `weather_data` is missing from the payload. Since the Public API Schema (`PHASE_0_CANON.md`, `PRD.md`) **does not allow** users to submit `weather_data`, *every* legitimate request triggers this fallback.
*   **Impact:** The `effective_level` calculation in `filter_and_score` creates a ceiling of **Low Confidence** for all traffic. The system cannot ever return "High" or "Medium" confidence recommendations in production.
*   **Violation:** Contradicts PRD Section 5.1 ("System-provided: Seasonal climate aggregates") and `PHASE_0_CANON.md` Section 2.1 (Input Schema). The system claims to look up climate data but instead defaults to a global static average.

### B. Test Suite Quality (CRITICAL)

*   **Issue:** **False Positive Testing (Schema Cheating)**
*   **Location:** `tests/test_inference_robustness.py`, `tests/test_fail_soft_compliance.py`, `src/validation/validate_inference.py`
*   **Description:** All tests inject a `weather_data` object into the request payload.
    ```python
    "weather_data": { "temperature": 25.0, ... } # ILLEGAL FIELD
    ```
*   **Why it matters:** This field is **not** in the public API contract. The tests are verifying a "God Mode" path that no real user can access. This effectively hides the "Implicit Degradation Trap" described above.
*   **Risk:** Deceptive CI/CD green lights.

### C. ML Model & Parameters (MAJOR)

*   **Issue:** **Unexplained Threshold Recalibration**
*   **Location:** `src/inference/predict.py` (Line 322)
*   **Description:** High Confidence threshold is set to `0.40` and Medium to `0.15`.
*   **Conflict:** `STEP_7_VALIDATION_REPORT.md` (Section 3.C) states the model is "skewed High" (>0.8 for 94% of cases).
    *   If the model is skewed high, a threshold of `0.40` is dangerously permissive (capturing 100% of outputs).
    *   However, `STEP_7` (Section 5.2) claims "Only 1.4% achieved High confidence," contradicting its own Section 3.C.
*   **Risk:** Probability semantics are completely incoherent. The thresholds appear to be "magic numbers" tuned to pass tests rather than derived from calibration data.

### D. Data Handling (MINOR)

*   **Issue:** **Global Weather Imputation**
*   **Location:** `src/inference/predict.py` -> `impute_weather_data`
*   **Description:** Uses static global averages (`_GLOBAL_WEATHER_STATS`) derived from training data for *all* missing weather.
*   **Impact:** This ignores the "Regional" aspect of the PRD entirely. A rice crop in a desert district will get the same "average" rainfall input as a rice crop in a monsoon district, leading to misleading feasibility scores.

---

## 3. Cross-Cutting Risks

1.  **Integration Mismatch:** Frontend/Backend teams following the `PRD.md` will send requests without `weather_data`. The API will accept them (Fail-Soft) but return garbage-quality confidence scores. Debugging this will be difficult because the error is semantic, not syntactic.
2.  **Over-Reliance on "Fail-Soft":** The system relies so heavily on "not crashing" that it fails to alert developers that it is operating in a permanently degraded state.

---

## 4. Alignment Scorecard

| Dimension | Score | Justification |
| :--- | :--- | :--- |
| **PRD Intent** | **Low** | "Auxiliary Intelligence" is effectively disabled by the weather data bug. |
| **Ethical Safety** | **High** | The system is extremely conservative (to a fault). It refuses to be confident. |
| **Robustness** | **Medium** | It doesn't crash, but it doesn't function correctly either. |
| **ML Correctness** | **Low** | Thresholds (0.40) seem arbitrary; Weather imputation removes all geographic signal. |
| **Integration Safety** | **Low** | The API implementation does not match the documented contract. |

---

## 5. Non-Blocking Observations

*   **Code Quality:** The code is generally clean, well-structured, and follows the project's style. `src/explainability` is well-implemented.
*   **Feature Parity:** `build_features.py` properly ensures training and inference use the same feature set.
*   **Documentation:** The `GENKIT.md` and `GEMINI.md` files are helpful context, though unrelated to the immediate failure.

---

## 6. Final Recommendation

**STATUS: NOT DEPLOYABLE**

The system cannot be deployed until the **Weather Data Gap** is resolved.

**Required Remediation:**
1.  **Implement Real Weather Lookup:** `impute_weather_data` must look up *actual* historical climate averages for the `region_id` (using `regional_profiles.csv` or a new artifact), rather than defaulting to global stats.
2.  **Fix Degradation Logic:** If the system performs a successful Regional Weather Lookup, it should return `DegradationLevel.EXACT_REGION` (or `STATE_FALLBACK`), **NOT** `NATIONAL_FALLBACK`.
3.  **Sanitize Tests:** Remove `weather_data` from all test payloads to force the tests to use the actual public API path. Ensure tests pass without this cheat.
4.  **Recalibrate Thresholds:** Re-verify the `0.40` threshold against the Validation Report's findings. If the model is overconfident, the threshold should be *higher* (e.g., 0.9), not lower.

**Once these steps are taken, a re-audit is required.**