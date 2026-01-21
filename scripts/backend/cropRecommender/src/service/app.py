import sys
import os
from fastapi import FastAPI, Body, HTTPException

# Adjust path to allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.inference.predict import predict

app = FastAPI(
    title="Crop Recommendation Inference Service",
    description="Auxiliary decision-support API for agricultural feasibility signals.",
    version="1.0.0"
)

@app.post("/predict")
def predict_endpoint(payload: dict = Body(...)):
    """
    Unified Inference Endpoint.
    Proxies request to the hardened src.inference.predict pipeline.
    """
    result = predict(payload)
    
    if result.get("status") == "error":
        msg = result.get("message", "Unknown error")
        # Distinguish Validation Errors vs Internal Errors based on message content prefix
        # predictable from predict.py
        if "Input Validation Error" in msg or "Missing" in msg:
            raise HTTPException(status_code=400, detail=msg)
        else:
            raise HTTPException(status_code=500, detail=msg)
            
    return result

@app.get("/health")
async def health_check():
    """Service health indicator."""
    return {"status": "healthy", "timestamp": os.getloadavg() if hasattr(os, 'getloadavg') else "available"}

"""
USAGE EXAMPLE:
--------------
Start service:
    uvicorn src.service.app:app --reload

Example Request:
    curl -X POST "http://localhost:8000/predict" \
         -H "Content-Type: application/json" \
         -d '{ 
               "user_context": {"region_id": "Satara", "season": "Kharif"},
               "soil_data": {"nitrogen": 90, "phosphorus": 42, "potassium": 43, "ph": 6.5}
             }'

Example Response:
    {
      "status": "success",
      "model_version": "v1.0.0",
      "meta": { ... },
      "recommendations": [ { "crop_name": "maize", "feasibility_score": 0.38, ... } ]
    }
"""
