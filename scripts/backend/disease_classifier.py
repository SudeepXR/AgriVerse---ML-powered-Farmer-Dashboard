import torch
from PIL import Image
import io
from transformers import pipeline

# This model is public and covers 38 classes (Rice, Tomato, Corn, etc.)
# No authentication (401 error) required.
MODEL_ID = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"

try:
    classifier = pipeline("image-classification", model=MODEL_ID)
except Exception as e:
    print(f"Error loading model: {e}")
    classifier = None

def diagnose_plant_image(image_bytes):
    if classifier is None:
        return {"status": "error", "message": "Model not loaded properly."}
        
    try:
        # Convert bytes to PIL Image
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Run prediction
        predictions = classifier(img)
        top_pred = predictions[0]
        
        # The model returns labels like "Tomato___Target_Spot" or "Rice___Leaf_Blast"
        label = top_pred['label']
        confidence = top_pred['score']
        
        # Split into Crop and Disease
        if "___" in label:
            parts = label.split("___")
            plant = parts[0].replace("_", " ")
            disease = parts[1].replace("_", " ")
        else:
            plant = "Unknown"
            disease = label.replace("_", " ")
            
        return {
            "status": "success",
            "plant": plant,
            "disease": disease,
            "confidence": f"{confidence:.2%}",
            "raw_label": label
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
