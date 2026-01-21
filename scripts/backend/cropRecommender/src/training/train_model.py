"""
Crop Recommender Model Training Pipeline.

This script trains the primary Random Forest Classifier and logs
validation metrics for auditing purposes.
"""

import json
import hashlib
import pickle
import os
import sys
import datetime
import csv

# Adjust path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.config import (
    PROCESSED_DIR, PROCESSED_TRAINING_FILE,
    ARTIFACTS_DIR, METADATA_DIR,
    FEATURES, TARGET,
    MODEL_VERSION, RANDOM_SEED, TEST_SPLIT_RATIO, MODEL_CONFIG
)

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score, classification_report
except ImportError:
    print("CRITICAL: scikit-learn not installed. Cannot train model.")
    sys.exit(1)

# ==========================================
# CONFIGURATION (Derived)
# ==========================================

PROCESSED_DATA_PATH = os.path.join(PROCESSED_DIR, PROCESSED_TRAINING_FILE)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_timestamp():
    return datetime.datetime.utcnow().isoformat() + "Z"

def compute_file_hash(filepath):
    """Computes SHA256 hash of a file for data versioning."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def load_data(filepath):
    """Loads processed CSV data."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Processed data not found at {filepath}")
    
    X = []
    y = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                feature_row = [float(row[f]) for f in FEATURES]
                X.append(feature_row)
                y.append(row[TARGET])
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to error: {e}")
                continue
                
    return X, y

def save_artifact(obj, filename):
    """Saves a python object (model) to disk."""
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    path = os.path.join(ARTIFACTS_DIR, filename)
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
    print(f"Saved artifact: {path}")
    return path

def save_metadata(metadata, filename):
    """Saves metadata JSON to disk."""
    os.makedirs(METADATA_DIR, exist_ok=True)
    path = os.path.join(METADATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata: {path}")
    return path

# ==========================================
# TRAINING PIPELINE
# ==========================================

def run_training():
    print(f"Starting Training Pipeline - Version {MODEL_VERSION}")
    print("=" * 50)
    
    # 1. Load Data
    print("Step 1: Loading Data...")
    X, y = load_data(PROCESSED_DATA_PATH)
    print(f"Loaded {len(X)} samples.")
    
    # 2. Train/Test Split (CRITICAL FIX)
    print(f"Step 2: Splitting Data ({int((1-TEST_SPLIT_RATIO)*100)}/{int(TEST_SPLIT_RATIO*100)} Train/Test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=TEST_SPLIT_RATIO, 
        random_state=RANDOM_SEED,
        stratify=y  # Ensure class distribution is preserved
    )
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    
    # 3. Compute Data Hash (Audit Trail)
    data_hash = compute_file_hash(PROCESSED_DATA_PATH)
    print(f"Data Hash: {data_hash}")
    
    # 4. Initialize Model
    print("Step 3: Initializing Primary Model (Random Forest)...")
    clf = RandomForestClassifier(**MODEL_CONFIG)
    
    # 5. Train Model (ON TRAINING SET ONLY)
    print("Step 4: Training...")
    clf.fit(X_train, y_train)
    
    # 6. Evaluate Model (ON HELD-OUT TEST SET)
    print("Step 5: Evaluating on Test Set...")
    y_pred = clf.predict(X_test)
    
    test_accuracy = accuracy_score(y_test, y_pred)
    test_f1_macro = f1_score(y_test, y_pred, average='macro')
    
    print("-" * 50)
    print("VALIDATION RESULTS:")
    print(f"  Test Accuracy:  {test_accuracy:.4f}")
    print(f"  Test F1-Macro:  {test_f1_macro:.4f}")
    print("-" * 50)
    
    # Optional: Detailed classification report
    # print(classification_report(y_test, y_pred))
    
    # 7. Save Artifacts
    print("Step 6: Saving Artifacts...")
    timestamp_safe = get_timestamp().replace(':', '-').replace('.', '-')
    artifact_filename = f"model_{MODEL_VERSION}_{timestamp_safe}.pkl"
    metadata_filename = f"meta_{MODEL_VERSION}_{timestamp_safe}.json"
    
    save_artifact(clf, artifact_filename)
    
    # 8. Generate Metadata (WITH NEW METRICS)
    metadata = {
        "model_version": MODEL_VERSION,
        "trained_on": get_timestamp(),
        "model_type": "RandomForestClassifier",
        "features": FEATURES,
        "target_classes": list(clf.classes_),
        "data_hash": data_hash,
        "training_config": MODEL_CONFIG,
        "random_seed": RANDOM_SEED,
        
        # NEW: Validation Metrics
        "test_split_ratio": TEST_SPLIT_RATIO,
        "test_samples": len(X_test),
        "train_samples": len(X_train),
        "test_accuracy": round(test_accuracy, 4),
        "test_f1_macro": round(test_f1_macro, 4),
        
        "prd_alignment": "Relative Feasibility Scoring Only. NOT Yield Prediction.",
        "artifact_path": artifact_filename
    }
    
    save_metadata(metadata, metadata_filename)
    
    print("=" * 50)
    print("Training Pipeline Complete.")
    print("AUDIT TRAIL:")
    print(f"  Model: {artifact_filename}")
    print(f"  Meta:  {metadata_filename}")
    print(f"  Accuracy: {test_accuracy:.4f} | F1: {test_f1_macro:.4f}")
    print("=" * 50)

if __name__ == "__main__":
    run_training()
