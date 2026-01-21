# Step 5 Canon: Model Selection

**Status:** APPROVED
**Date:** 2026-01-20
**Scope:** `src/training/`, `src/inference/`

---

## 1. Candidate Evaluation

We evaluated two model families against the core mandates of **Interpretability**, **Stability**, and **Ethical Restraint**.

### Candidate A: Regularized Logistic Regression (Multi-Class)
*   **Interpretability:** High. Coefficients map directly to feature influence (e.g., "High Nitrogen increases score for Rice").
*   **Stability:** High. Linear boundaries degrade gracefully with noisy inputs.
*   **Output:** Naturally produces probability-like scores ($0.0 - 1.0$) via Softmax.
*   **Risk:** May underfit complex non-linear interactions (e.g., if a crop needs High N *but* Low pH).

### Candidate B: Shallow Tree Ensemble (Random Forest / Gradient Boosting)
*   **Configuration:** Max Depth ≤ 3, limited estimators.
*   **Interpretability:** Medium-High. Feature importance is available, but specific logic paths are harder to trace than linear weights.
*   **Stability:** Medium. Decision boundaries are step-functions, which can cause sudden jumps in ranking with small input changes.
*   **Output:** Can produce scores, but often pushed towards extremes (0 or 1) without calibration.
*   **Risk:** Prone to overfitting on small datasets if not heavily constrained.

---

## 2. Primary Model Selection

**DECISION:** The Primary Model shall be **Random Forest Classifier (Shallow)**.

### Justification
While Logistic Regression is the most interpretable, agricultural suitability is inherently **non-linear**.
*   *Example:* A crop might tolerate high temperature *only if* humidity is also high. Linear models struggle with these "AND" conditions without manual interaction features.
*   **Shallow Trees** (Depth ≤ 5) capture these interactions naturally while remaining interpretable enough for our needs.
*   **Random Forest** specifically is chosen over Gradient Boosting for its robustness to noise and reduced tendency to overfit on small datasets (2200 rows).

### Implementation Constraints
To maintain the "Auxiliary" nature of the system, the Random Forest implementation **MUST**:
1.  Set `max_depth` $\le 10$ (Prevent memorization).
2.  Set `n_estimators` $\approx 100$ (Standard stability).
3.  Use `predict_proba()` to generate the similarity scores.
4.  **NEVER** use the hard class prediction (`predict()`) as the final output.

---

## 3. Secondary Model (Experimental)

**Selection:** **Logistic Regression**
*   **Role:** Baseline Baseline.
*   **Usage:** During training, we will train a Logistic Regression model alongside the Random Forest.
*   **Condition:** If the Random Forest performance is not significantly better (>5% accuracy gain), we **MUST** revert to Logistic Regression for its superior transparency.
*   **Status:** Fallback only.

---

## 4. Forbidden Models

The following architectures are explicitly **BANNED** for this project:

| Model Family | Reason for Ban |
| :--- | :--- |
| **Deep Neural Networks** | **Black Box Risk.** Impossible to explain *why* a recommendation was made to a farmer. Requires far more data than we have. |
| **k-Nearest Neighbors (k-NN)** | **Inference Latency & Scale.** Requires storing training data at inference time. Curse of dimensionality with inputs. |
| **Full-Depth XGBoost/LightGBM** | **False Precision.** Highly complex boundaries imply a level of certainty about the "perfect" conditions that does not exist in reality. |
| **Support Vector Machines (SVM)** | **Output Semantics.** Standard SVMs do not naturally produce probabilistic scores. |

---

## 5. Final Decision Statement

> The system will utilize a **Shallow Random Forest Classifier** to generate crop feasibility scores.
> This model balances the need to capture non-linear agricultural interactions (e.g., heat + humidity) with the strict requirement for **interpretability and robustness**.
> We prioritize a model that provides **smooth, defensible rankings** over one that chases marginal accuracy gains through opacity.
> The output is mathematically a probability estimate but semantically a **similarity score**.

---
*End of Canon. Any deviation requires a formal Request for Comment (RFC).*
