# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Crop Feasibility Inference Service - an auxiliary decision-support tool that provides probabilistic crop feasibility insights based on regional historical data and soil profiles. It acts as a "Similarity Ranker," comparing current conditions to successful historical patterns. The system prioritizes transparency, robustness, and farmer autonomy over prescriptive recommendations.

**Critical Design Constraint**: ML outputs are informational signals only - never guarantees or authoritative recommendations.

## Common Commands

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Feature Engineering (generates regional_profiles.csv, ml_training.csv, seasonality_log.csv)
python -m src.training.build_features

# Train Model
python -m src.training.train_model

# Run API Server
uvicorn src.service.app:app --reload

# Run All Tests
pytest tests/

# Run Single Test File
pytest tests/test_fail_soft_compliance.py

# Validate Inference Pipeline
python src/validation/validate_inference.py
```

## Architecture

### 4-Phase Hybrid Inference Pipeline

The inference logic in `src/inference/predict.py` follows a strict execution order:

1. **Phase 1: Regional Feasibility Filter** (Non-ML) - Rejects crops not historically grown in the region using `regional_profiles.csv`
2. **Phase 2: Contextual Refinement** (Heuristic) - Filters crops incompatible with the current season using `seasonality_log.csv`
3. **Phase 3: Similarity Scoring** (ML) - Random Forest classifier scores remaining candidates based on soil/weather alignment
4. **Phase 4: Post-Processing** - Applies confidence caps, generates explanations, appends warnings

### Fail-Soft Degradation Strategy

Defined in `src/inference/degradation.py` with three levels:

| Level | Trigger | Confidence Cap |
|-------|---------|----------------|
| `EXACT_REGION` | District found in reference data | High |
| `STATE_FALLBACK` | District unknown, state valid | Medium |
| `NATIONAL_FALLBACK` | Region completely unknown | Low |

### Key Modules

- `src/config.py` - **Source of truth** for all thresholds, paths, feature definitions (ensures parity between training and inference)
- `src/inference/predict.py` - Main inference pipeline with input validation and output schema enforcement
- `src/inference/degradation.py` - Degradation level enum and confidence capping logic
- `src/training/build_features.py` - Generates processed data files from raw datasets
- `src/training/train_model.py` - Trains Random Forest with 80/20 train/test split
- `src/explainability/generate_reasons.py` - Converts ML signals to human-readable, non-authoritative text
- `src/service/app.py` - FastAPI endpoint (`POST /predict`)

### Data Flow

Raw datasets → `build_features.py` → Processed files (`data/processed/`) → `train_model.py` → Model artifacts (`models/artifacts/`) → `predict.py` uses both model and processed reference files

## Design Constraints

1. **Non-Authoritative Language**: Never use phrases like "best crop", "will grow well", or output probabilities. Use "conditions align", "similar to history" instead.

2. **Fail-Soft over Fail-Fast**: Handle missing soil_data or unknown regions gracefully with imputation + warnings rather than errors. Only fail fast on missing `region_id` or partial soil data.

3. **Weather Imputation Only**: Users cannot provide weather data - it's always derived from regional historical averages to prevent gaming the model.

4. **Schema Enforcement**: All API responses are validated against `data/schemas/inference_output.schema.json` at runtime.

5. **Configuration Centralization**: All thresholds (confidence levels, feature names, paths) must come from `src/config.py` - no magic strings in other modules.
