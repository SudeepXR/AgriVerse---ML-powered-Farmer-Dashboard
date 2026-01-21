# Crop Feasibility Inference Service

> **Auxiliary Intelligence for Farmer Decision Support**

This service provides probabilistic crop feasibility insights based on regional historical data and soil profiles. It acts as a "Similarity Ranker," comparing current conditions to successful historical patterns.

**⚠️ Disclaimer:** This system provides informational insights only. It does NOT predict yield, profit, or guarantee success. It is not a substitute for professional agronomic advice.

---

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Prepare Data (Feature Engineering)
```bash
python -m src.training.build_features
# Generates regional_profiles.csv, ml_training.csv, seasonality_log.csv
```

### Train Model (with Validation)
```bash
python -m src.training.train_model
# Verify "VALIDATION RESULTS" in output
```

### Run Server
```bash
uvicorn src.service.app:app --reload
```

### Make a Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{ "user_context": { "region_id": "Satara" } }'
```

---

## 📚 Documentation Map

*   **[DESIGN.md](DESIGN.md)**: The authoritative guide to System Architecture, ML Logic, and the Fail-Soft Strategy. **Start here.**
*   **[PRD.md](PRD.md)**: Product Vision, User Goals, and Constraints.
*   **[DATA_MANIFEST.md](DATA_MANIFEST.md)**: Details on the datasets used for training and inference.
*   **[CONTRIBUTING.md](CONTRIBUTING.md)**: Developer setup, testing, and validation guides.
*   **`docs/`**: Validation reports and historical audit logs.

---

## 🛠️ Key Features

*   **Hybrid Pipeline:** Combines strict regional filtering with ML-based similarity scoring.
*   **Fail-Soft Architecture:** Gracefully handles missing soil data or unknown regions via a defined degradation hierarchy.
*   **Safety Guardrails:** Confidence caps prevent over-certainty in low-data scenarios.
*   **Explainability:** Every recommendation includes reasoning transparency.

---

## ⚖️ License & Philosophy

This project adheres to a strict "Human-in-the-Loop" philosophy. Machine Learning is used to aggregate weak signals, not to replace human judgment. See `DESIGN.md` for details.