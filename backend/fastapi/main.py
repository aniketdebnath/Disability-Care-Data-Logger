from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ml_service import process_signal  # Traditional models
from process_service import process_ppg_signal  # Traditional signal processing
from lstm_process_service import process_bvp_signal  # LSTM-specific signal processing
from lstm_service import predict_lstm  # LSTM prediction

app = FastAPI()

# Define input schema for raw PPG signal
class PPGSignalInput(BaseModel):
    IRLED: str

# Define input schema for ML model
class PPGProcessedData(BaseModel):
    rr_interval: float
    heart_rate: float
    sdnn: float
    sdsd: float

# Define response schema for ML predictions
class PredictionResponse(BaseModel):
    combined_prediction: str
    reliability_score: str
    model_predictions: dict
    lstm_prediction: str
    lstm_confidence: float
    explanation: str
    message: str

# Automate Process and Prediction for both traditional and LSTM
@app.post("/process_and_detect", response_model=PredictionResponse)
def process_and_detect(signal: PPGSignalInput):
    try:
        # Step 1: Process the PPG signal for traditional models
        rr_interval, heart_rate, sdnn, sdsd = process_ppg_signal(signal.IRLED)

        # Ensure processing was successful
        if rr_interval is None or heart_rate is None:
            raise HTTPException(status_code=400, detail="Failed to process PPG signal")

        # Step 2: Use the processed data for traditional anomaly detection
        traditional_result = process_signal(rr_interval, heart_rate, sdnn, sdsd)

        # Step 3: Process the BVP signal specifically for LSTM (this returns LSTM-ready sequences)
        bvp_sequences = process_bvp_signal(signal.IRLED)
        print(f"DEBUG: BVP sequences shape for LSTM: {bvp_sequences.shape}")

        # Step 4: Use the processed BVP data with LSTM for prediction
        lstm_result = predict_lstm(bvp_sequences)
        print(f"DEBUG: LSTM prediction result: {lstm_result}")

        # Verify LSTM prediction format
        lstm_prediction = lstm_result["lstm_prediction"] if "lstm_prediction" in lstm_result else "Unknown"
        lstm_confidence = lstm_result["confidence_score"] if "confidence_score" in lstm_result else 0.0

        # Combine results from traditional and LSTM models
        return {
            "combined_prediction": traditional_result["combined_prediction"],
            "reliability_score": traditional_result["reliability_score"],
            "model_predictions": traditional_result["model_predictions"],
            "lstm_prediction": lstm_prediction,
            "lstm_confidence": lstm_confidence,
            "explanation": traditional_result["explanation"],
            "message": "Combined prediction successful"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PPG Processing Endpoint
@app.post("/process", response_model=PPGProcessedData)
def process_ppg(signal: PPGSignalInput):
    try:
        rr_interval, heart_rate, sdnn, sdsd = process_ppg_signal(signal.IRLED)
        return {
            "rr_interval": rr_interval,
            "heart_rate": heart_rate,
            "sdnn": sdnn,
            "sdsd": sdsd
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ML Prediction Endpoint
@app.post("/detect", response_model=PredictionResponse)
def detect_anomaly(data: PPGProcessedData):
    try:
        result = process_signal(data.rr_interval, data.heart_rate, data.sdnn, data.sdsd)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Health check endpoint
@app.get("/")
def read_root():
    return {"status": "FastAPI is running!"}
