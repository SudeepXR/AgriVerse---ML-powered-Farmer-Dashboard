import os
import sys
import json
import pickle
import numpy as np
import csv
import random
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

ARTIFACTS_DIR = "models/artifacts"
PROCESSED_DATA_PATH = "data/processed/ml_training.csv"
VALIDATION_OUTPUT_DIR = "src/validation/reports"
FEATURES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
TARGET = 'label'
RANDOM_SEED = 42
TOP_K = 3

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_latest_model():
    files = [f for f in os.listdir(ARTIFACTS_DIR) if f.endswith('.pkl')]
    if not files:
        raise FileNotFoundError("No model artifacts found.")
    # Sort by timestamp in filename (assuming ISO format in name)
    latest_file = sorted(files)[-1]
    path = os.path.join(ARTIFACTS_DIR, latest_file)
    print(f"Loading model: {path}")
    with open(path, 'rb') as f:
        model = pickle.load(f)
    return model

def load_data(filepath):
    X = []
    y = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                feature_row = [float(row[f]) for f in FEATURES]
                X.append(feature_row)
                y.append(row[TARGET])
            except:
                continue
    return np.array(X), np.array(y)

def get_top_k_indices(probs, k=3):
    """Returns indices of top K classes for each sample."""
    # argsort sorts ascending, so we take last k and reverse
    return np.argsort(probs, axis=1)[:, -k:][:, ::-1]

def jaccard_similarity(list1, list2):
    """Calculates overlap between two lists of items."""
    s1 = set(list1)
    s2 = set(list2)
    if not s1 and not s2: return 1.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

# ==========================================
# VALIDATION MODULES
# ==========================================

def validate_ranking_stability(model, X, y, classes):
    print("\n[A] Running Ranking Stability Test...")
    
    # 1. Baseline Predictions
    base_probs = model.predict_proba(X)
    base_top_k = get_top_k_indices(base_probs, k=TOP_K)
    
    # 2. Perturb Inputs (Simulate 5% measurement noise)
    noise_level = 0.05
    noise = np.random.normal(0, noise_level, X.shape) * X
    X_perturbed = X + noise
    
    # 3. Perturbed Predictions
    pert_probs = model.predict_proba(X_perturbed)
    pert_top_k = get_top_k_indices(pert_probs, k=TOP_K)
    
    # 4. Measure Stability
    stabilities = []
    for i in range(len(X)):
        # Convert indices to class names for stability check
        base_crops = [classes[idx] for idx in base_top_k[i]]
        pert_crops = [classes[idx] for idx in pert_top_k[i]]
        score = jaccard_similarity(base_crops, pert_crops)
        stabilities.append(score)
        
    avg_stability = np.mean(stabilities)
    print(f"  Average Top-{TOP_K} Overlap under 5% Noise: {avg_stability:.4f}")
    
    return {
        "test": "ranking_stability",
        "noise_level": noise_level,
        "avg_top_k_overlap": avg_stability,
        "interpretation": "High overlap (>0.8) indicates robust decision boundaries."
    }

def validate_noise_sensitivity(model, X, classes):
    print("\n[B] Running Noise Sensitivity Test...")
    
    # Select a few random samples
    indices = np.random.choice(len(X), 5, replace=False)
    samples = X[indices]
    
    results = []
    
    for i, sample in enumerate(samples):
        # Original
        prob_orig = model.predict_proba([sample])[0]
        max_conf_orig = np.max(prob_orig)
        
        # Degraded (e.g. Missing soil data -> Imputed with wide variance noise)
        # Here we simulate extreme noise on N/P/K (indices 0,1,2)
        sample_noisy = sample.copy()
        # Add large noise to NPK to simulate bad imputation
        sample_noisy[0:3] += np.random.normal(0, 50, 3) 
        
        prob_noisy = model.predict_proba([sample_noisy])[0]
        max_conf_noisy = np.max(prob_noisy)
        
        results.append({
            "sample_id": int(indices[i]),
            "original_max_conf": float(max_conf_orig),
            "noisy_max_conf": float(max_conf_noisy),
            "drop": float(max_conf_orig - max_conf_noisy)
        })
        
    avg_drop = np.mean([r['drop'] for r in results])
    print(f"  Avg Confidence Drop under Heavy NPK Noise: {avg_drop:.4f}")
    
    return {
        "test": "noise_sensitivity",
        "details": results,
        "avg_confidence_drop": avg_drop,
        "interpretation": "Positive drop means model becomes less certain with bad inputs (Good)."
    }

def validate_calibration(model, X, classes):
    print("\n[C] Running Confidence Distribution Test (Calibration Proxy)...")
    
    probs = model.predict_proba(X)
    max_confs = np.max(probs, axis=1)
    
    # Bin the confidences
    hist, bins = np.histogram(max_confs, bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0])
    
    dist = {
        "0.0-0.2": int(hist[0]),
        "0.2-0.4": int(hist[1]),
        "0.4-0.6": int(hist[2]),
        "0.6-0.8": int(hist[3]),
        "0.8-1.0": int(hist[4])
    }
    
    print(f"  Confidence Distribution: {dist}")
    
    return {
        "test": "confidence_distribution",
        "distribution": dist,
        "interpretation": "Should not be clustered solely at 1.0. Spread implies healthy uncertainty."
    }

# ==========================================
# MAIN
# ==========================================

def run_validation():
    ensure_dir(VALIDATION_OUTPUT_DIR)
    
    model = load_latest_model()
    X, y = load_data(PROCESSED_DATA_PATH)
    classes = model.classes_
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "model_type": type(model).__name__,
        "validation_results": []
    }
    
    # Run Tests
    res_a = validate_ranking_stability(model, X, y, classes)
    report["validation_results"].append(res_a)
    
    res_b = validate_noise_sensitivity(model, X, classes)
    report["validation_results"].append(res_b)
    
    res_c = validate_calibration(model, X, classes)
    report["validation_results"].append(res_c)
    
    # Save Report
    out_path = os.path.join(VALIDATION_OUTPUT_DIR, "validation_results.json")
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"\nValidation Complete. Results saved to {out_path}")

if __name__ == "__main__":
    np.random.seed(RANDOM_SEED)
    run_validation()
