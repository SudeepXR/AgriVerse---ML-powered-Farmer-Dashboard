"""
Centralized Configuration for Crop Recommender System.

This module consolidates all shared constants, file paths, and hyper-parameters
to avoid "magic strings" scattered across the codebase.
"""

# ==========================================
# FILE PATHS
# ==========================================

# Raw Data
RAW_DIR = "data/raw"
RAW_TRAINING_FILE = "Crop_recommendation.csv"
RAW_REGIONAL_FILE = "CropDataset-Enhanced.csv"
RAW_HISTORICAL_FILE = "crop_production.csv"
RAW_WEATHER_HISTORICAL_FILE = "Custom_Crops_yield_Historical_Dataset.csv"

# Processed Data
PROCESSED_DIR = "data/processed"
PROCESSED_TRAINING_FILE = "ml_training.csv"
REGIONAL_PROFILES_FILE = "regional_profiles.csv"
SEASONALITY_FILE = "seasonality_log.csv"

# Model Artifacts
ARTIFACTS_DIR = "models/artifacts"
METADATA_DIR = "models/metadata"
SCHEMA_PATH = "data/schemas/inference_output.schema.json"

# ==========================================
# FEATURE ENGINEERING
# ==========================================

# Approved Feature List (Order MUST match training and inference)
FEATURES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
TARGET = 'label'

# ==========================================
# TRAINING HYPERPARAMETERS
# ==========================================

MODEL_VERSION = "v1.1.0"  # Bumped for validated training
RANDOM_SEED = 42
TEST_SPLIT_RATIO = 0.20  # 80% train, 20% test

MODEL_CONFIG = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": RANDOM_SEED,
    "n_jobs": -1
}

# ==========================================
# INFERENCE THRESHOLDS
# ==========================================

# Confidence Level Thresholds
# NOTE: These are initial heuristic values. Ideally, calibrate using
# validation set percentiles after producing a validated model.
# score >= HIGH_THRESHOLD -> "High"
# score >= MEDIUM_THRESHOLD -> "Medium"
# else -> "Low"
HIGH_CONFIDENCE_THRESHOLD = 0.70
MEDIUM_CONFIDENCE_THRESHOLD = 0.35
