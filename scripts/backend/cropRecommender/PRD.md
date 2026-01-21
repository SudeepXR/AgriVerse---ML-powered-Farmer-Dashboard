# Product Requirements Document (PRD)
## Project: Farmer Decision-Support System with Auxiliary Crop Intelligence

---

## 1. Purpose & Vision

### 1.1 Problem Statement
Farmers make crop-selection decisions under high uncertainty due to climate variability, regional constraints, and incomplete information. Existing tools often provide prescriptive recommendations without communicating uncertainty or context.

This project aims to **support human decision-making**, not replace it.

---

### 1.2 Product Vision
To build a **farmer-centric decision-support system** that:
- Aggregates historical and contextual signals
- Surfaces **multiple feasible crop options**
- Communicates uncertainty clearly
- Uses machine learning as an **auxiliary insight generator**, not an authority

The system prioritizes transparency, robustness, and farmer autonomy.

---

## 2. Role of Machine Learning

### 2.1 Positioning of ML
Machine learning is **not the centerpiece** of this system.

The ML model:
- Generates feasibility scores or rankings
- Aggregates imperfect signals probabilistically
- Supports comparison, not prescription

The ML model does **not**:
- Output a single “best crop”
- Guarantee outcomes
- Replace agronomic expertise

---

### 2.2 Rationale for Using ML
ML is used because it:
- Handles noisy and incomplete data better than rule-based logic
- Integrates multiple weak signals
- Degrades gracefully under uncertainty
- Can be retrained as data evolves

ML is explicitly **not used to claim superior decision-making authority**.

---

## 3. Target Users

### Primary Users
- Farmers with basic digital access
- Agricultural students or extension workers (pilot users)

### Secondary Users
- Researchers
- Policy or planning stakeholders (exploratory use)

---

## 4. User Goals

Users should be able to:
- Understand which crops are **feasible** under current conditions
- Compare trade-offs between options
- Reduce decision uncertainty
- Retain full control over final decisions

---

## 5. Core Features

### 5.1 Input Module
**User-provided (optional and approximate):**
- Region / district
- Season
- Soil type (categorical, optional)
- Irrigation availability (optional)

**System-provided:**
- Historical crop presence
- Seasonal climate aggregates
- Soil classification metadata (where available)

---

### 5.2 Crop Feasibility Insights
The system provides:
- A **ranked list of feasible crops**
- Relative feasibility scores
- Confidence indicators (low / medium / high)
- High-level reasoning

Example framing:
> “Under similar historical conditions, these crops have been commonly grown in this region. Actual outcomes may vary.”

---

### 5.3 Explainability Layer
For each crop option:
- Key contributing factors (e.g., season compatibility, regional persistence)
- Simple, non-technical explanations

Explainability prioritizes **interpretability over model complexity**.

---

### 5.4 Uncertainty & Risk Signaling
- Confidence levels based on data coverage
- Warnings for missing or unreliable inputs
- Explicit avoidance of guaranteed language

---

## 6. Non-Goals (Out of Scope)

The system will **not**:
- Predict exact yields
- Optimize for profit
- Provide financial or agronomic guarantees
- Automate final crop decisions
- Replace experts or advisors

---

## 7. Functional Requirements

- **FR-1:** System shall accept incomplete user inputs.
- **FR-2:** System shall output multiple crop options.
- **FR-3:** System shall provide explanations for outputs.
- **FR-4:** System shall label ML outputs as informational insights.
- **FR-5:** System shall include uncertainty or confidence indicators.

---

## 8. Non-Functional Requirements

### Interpretability
Models must support feature attribution or explainable logic.

### Robustness
System must handle noisy inputs and missing data gracefully.

### Accessibility
Outputs must be understandable by non-technical users.

### Ethics
The system must avoid authoritative or prescriptive claims.

---

## 9. Data Strategy

### 9.1 Initial Phase
Use publicly available datasets such as:
- Historical crop area and production (district/season level)
- Long-term climate aggregates
- Soil classification maps

Data is used to infer **relative feasibility**, not outcomes.

---

### 9.2 Future Phase (Optional)
- User feedback (opt-in)
- Periodic model retraining
- Regional specialization

No automated learning from user inputs in early versions.

---

## 10. Model Design Principles

- Prefer simple, interpretable models
- Focus on ranking rather than classification
- Output probabilistic or relative scores
- Avoid false precision

---

## 11. Evaluation Metrics

### Quantitative
- Stability of rankings under noisy inputs
- Inclusion rate of user-chosen crops
- Confidence calibration

### Qualitative
- User understanding
- Perceived usefulness
- Appropriate trust (no over-reliance)

---

## 12. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Over-trust in ML | Multiple options + cautious language |
| Poor data quality | Confidence signaling |
| Climate drift | Periodic retraining |
| Low novelty perception | Clear decision-support framing |

---

## 13. Success Criteria

The system is successful if:
- Users feel more informed, not directed
- Uncertainty is reduced, not hidden
- ML adds value without dominating decisions
- Outputs are transparent and defensible

---

## 14. Summary

This project does not attempt to predict agricultural outcomes.

It aims to **support informed human judgment under uncertainty**, using machine learning as a responsible, secondary tool.

Machine learning is treated as:
> *A way to synthesize imperfect information — not a source of truth.*
