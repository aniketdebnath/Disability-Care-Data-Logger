# fastapi_app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ml_service import process_signal
from process_service import process_ppg_signal

app = FastAPI()

# Define input schema for raw PPG signal
# class PPGSignalInput(BaseModel):
#     _id: str
#     DeviceID: str
#     DateTime: str
#     GreenLED: str

# Define input schema for raw PPG signal
class PPGSignalInput(BaseModel):
    GreenLED: str

# Define input schema for ML model
class PPGProcessedData(BaseModel):
    rr_interval: float
    heart_rate: float

# Define response schema for ML predictions
class PredictionResponse(BaseModel):
    svm_prediction: int
    svm_confidence: float
    rf_prediction: int
    rf_confidence: float
    rf_feature_importance: dict
    knn_prediction: int
    knn_confidence: float
    message: str

# Automate Process and Prediction
@app.post("/process_and_detect", response_model=PredictionResponse)
def process_and_detect(signal: PPGSignalInput):
    try:
        # Step 1: Process the PPG signal to extract RR Interval and Heart Rate
        rr_interval, heart_rate = process_ppg_signal(signal.GreenLED)

        if rr_interval is None or heart_rate is None:
            raise HTTPException(status_code=400, detail="Failed to process PPG signal")

        # Step 2: Use the processed data for anomaly detection
        result = process_signal(rr_interval, heart_rate)

        # Return the detailed result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PPG Processing Endpoint
@app.post("/process", response_model=PPGProcessedData)
def process_ppg(signal: PPGSignalInput):
    try:
        rr_interval, bpm = process_ppg_signal(signal.GreenLED)
        return {"rr_interval": rr_interval, "heart_rate": bpm}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ML Prediction Endpoint
@app.post("/detect", response_model=PredictionResponse)
def detect_anomaly(data: PPGProcessedData):
    try:
        result = process_signal(data.rr_interval, data.heart_rate)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#Health check endpoint
@app.get("/")
def read_root():
    return {"status": "FastAPI is running!"}
