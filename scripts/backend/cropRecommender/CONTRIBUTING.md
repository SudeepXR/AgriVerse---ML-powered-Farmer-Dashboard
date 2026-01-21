# Contributing to Crop Recommender

Welcome! This is an auxiliary decision-support system for agricultural insights.

## 1. Project Structure

```
├── src/
│   ├── inference/    # Core logic (predict.py, degradation.py)
│   ├── service/      # API entry point (app.py)
│   └── training/     # Model training scripts
├── tests/            # Pytest suite
├── data/             # Datasets & Schemas
├── models/           # Serialized artifacts (.pkl)
└── docs/             # Reports & Archive
```

## 2. Setup & Installation

**Prerequisites:** Python 3.9+

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

## 3. Running the Service

```bash
uvicorn src.service.app:app --reload
```
API Docs will be available at: `http://localhost:8000/docs`

## 4. Testing

We maintain a strict test suite to ensure safety and contract compliance.

```bash
# Run all unit tests
pytest tests/
```

**Key Test Files:**
*   `tests/test_inference_robustness.py`: Checks happy paths & missing inputs.
*   `tests/test_fail_soft_compliance.py`: Checks degradation logic & fail-soft safety.

## 5. Validation

Before submitting changes, run the validation script to ensure confidence calibration hasn't drifted.

```bash
python src/validation/validate_inference.py
```

## 6. Contribution Standards

*   **No "Best Crop":** Never use authoritative language in output strings.
*   **Fail-Soft:** Always handle missing `soil_data` or unknown regions gracefully.
*   **Design Alignment:** Read `DESIGN.md` before changing core logic.
*   **Schema:** Do not alter the Public API contract without a major version update.
