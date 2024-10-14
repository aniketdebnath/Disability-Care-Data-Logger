# Disability Care Data Logger - FastAPI Service

This FastAPI-based service processes PPG signals, detects anomalies in heart rate, and predicts abnormal conditions using machine learning models (SVM, KNN, and Random Forest). The backend is integrated with a Node.js server, which monitors MongoDB for real-time data and sends PPG signals for processing.

## Features

- **Process PPG Signals:** Extracts RR Interval and Heart Rate from raw PPG signals.
- **Anomaly Detection:** Uses SVM, KNN, and Random Forest models to predict anomalies.
- **Machine Learning Models:** Pre-trained models (SVM, RF, KNN) are used for heart rate anomaly detection.
- **REST API:** Exposes endpoints to process signals and return predictions.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn (for running the FastAPI app)
- Pydantic (for input validation)
- Joblib (for loading ML models)
- Pandas (for data manipulation)
- NumPy (for numerical operations)
- HeartPy (for heart rate analysis)
- Scipy (for signal processing)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/disability-care-data-logger.git
cd disability-care-data-logger/backend/fastapi
```
