import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks
from pymongo import MongoClient
from tensorflow.keras.models import load_model
import joblib
from fastapi import FastAPI, HTTPException
from sklearn.metrics import mean_squared_error
import math
import logging
from datetime import datetime
from fastapi import Query

# Configure logging
logging.basicConfig(level=logging.INFO)
app = FastAPI()

# MongoDB connection
try:
    mongo_client = MongoClient("mongodb+srv://FYPUSERS:k1iTgwyFFzGlAkeN@fyptestdb.d7zdlnq.mongodb.net/FYPData")
    db = mongo_client['FYPData']
    collection = db['HealthData']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Step 1: Bandpass filter for noise reduction
def bandpass_filter(data, lowcut, highcut, sample_rate, order=2):
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

# Step 2: Detect peaks in the filtered PPG signal
def detect_peaks(ppg_data, sample_rate):
    peaks, _ = find_peaks(ppg_data, distance=sample_rate * 0.5)  # Assuming min heart rate 30 bpm
    return peaks

# Step 3: Calculate IBI from detected peaks
def calculate_ibi_from_peaks(peaks, sample_rate):
    if len(peaks) > 1:
        ibi_intervals = np.diff(peaks) / sample_rate * 1000  # Convert to milliseconds
        return ibi_intervals
    else:
        return []

# Step 4: Process IR LED signal and extract IBI values
def process_ir_led_signal(ir_led_data, sample_rate=125):
    # Apply bandpass filter to clean up noise
    filtered_data = bandpass_filter(ir_led_data, lowcut=0.67, highcut=3.0, sample_rate=sample_rate)
    
    # Detect peaks in the filtered signal
    peaks = detect_peaks(filtered_data, sample_rate)
    
    # Calculate IBI values
    ibi_intervals = calculate_ibi_from_peaks(peaks, sample_rate)
    return ibi_intervals

# Helper functions to process the LED data
def process_led_data(led_data: str):
    """ Convert the LED data from string to a list of integers """
    return [int(i) for i in led_data.split(',') if i.isnumeric()]

# Helper to make data JSON serializable
def make_serializable(data):
    if isinstance(data, dict):
        return {k: make_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_serializable(item) for item in data]
    elif isinstance(data, (np.int64, np.int32)):
        return int(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, pd.Timestamp):
        return str(data)
    return data

# Load the LSTM model and scaler
lstm_model = load_model('models/lstm_model_ms_seq_10_new.h5',compile=False)
scaler = joblib.load('models/scaler_ms_seq_10_new.pkl')

# Load the Random Forest model
rf_model = joblib.load('models/random_forest_model_detected_peaks.pkl')

# Prepare IBI sequences for LSTM model input
def prepare_lstm_data(ibi_values, sequence_length=10):
    sequences = []
    for i in range(len(ibi_values) - sequence_length):
        sequences.append(ibi_values[i:i + sequence_length])
    return np.array(sequences)

# Prepare IBI sequences for Random Forest input
def prepare_rf_data(ibi_values, sequence_length=10):
    X = []
    for i in range(len(ibi_values) - sequence_length):
        X.append(ibi_values[i:i + sequence_length])
    return np.array(X)

# Predict IBI values using the LSTM model
def predict_lstm(ibi_values, sequence_length=10):
    ibi_values = np.array(ibi_values).reshape(-1, 1)  # Reshape to (n_samples, 1)
    ibi_scaled = scaler.transform(ibi_values)
    X_sequences = prepare_lstm_data(ibi_scaled, sequence_length=sequence_length)
    
    if X_sequences.size == 0:
        return np.array([])  # Return empty array if no sequences are available
    
    y_pred_scaled = lstm_model.predict(X_sequences)
    y_pred = scaler.inverse_transform(y_pred_scaled).flatten()
    
    return y_pred

# Predict IBI values using the Random Forest model
def predict_rf(ibi_values, sequence_length=10):
    ibi_values = np.array(ibi_values).reshape(-1, 1)  # Reshape to (n_samples, 1)
    X_sequences = prepare_rf_data(ibi_values.flatten(), sequence_length=sequence_length)
    
    if X_sequences.size == 0:
        return np.array([])  # Return empty array if no sequences are available
    
    y_pred = rf_model.predict(X_sequences)
    
    return y_pred

# Calculate Heart Rate from IBI values
def calculate_hr(ibi_values):
    ibi_values = np.array(ibi_values)
    hr = 60000 / ibi_values  # HR in BPM
    return hr

# Helper function to get a single HR value (mean or median)
def get_single_hr_value(hr_values):
    if len(hr_values) > 0:
        return np.mean(hr_values)  # You can change this to np.median(hr_values) if needed
    return None

@app.get("/process-mongodb-data")
def process_mongodb_data(deviceId: str = Query(None)):
    try:
        # Log the deviceId to confirm it's received correctly
        logging.info(f"Filtering data for device ID: {deviceId}")

        # Prepare MongoDB query
        query = {}
        if deviceId:
            query = {"DeviceID": deviceId}

        # Retrieve data from MongoDB using the query filter
        data_cursor = collection.find(query)
        data_list = list(data_cursor)

        if not data_list:
            raise HTTPException(status_code=404, detail="No data found for the specified device ID")

        # Convert MongoDB data to pandas DataFrame
        df = pd.DataFrame(data_list)

        # Process each LED data column (IRLED) and calculate IBI values
        df['IRLED_processed'] = df['IRLED'].apply(process_led_data)
        df['IBI_values'] = df['IRLED_processed'].apply(lambda ir_led: process_ir_led_signal(ir_led, sample_rate=125))

        # Predict IBI values using LSTM and Random Forest
        df['Predicted_IBI_LSTM'] = df['IBI_values'].apply(lambda ibi: predict_lstm(ibi, sequence_length=10) if len(ibi) >= 10 else [])
        df['Predicted_IBI_RF'] = df['IBI_values'].apply(lambda ibi: predict_rf(ibi, sequence_length=10) if len(ibi) >= 10 else [])

        # Calculate HR values from actual, LSTM-predicted, and RF-predicted IBI values
        df['Actual_HR_List'] = df['IBI_values'].apply(lambda ibi: calculate_hr(ibi) if len(ibi) > 0 else [])
        df['Predicted_HR_List_LSTM'] = df['Predicted_IBI_LSTM'].apply(lambda ibi: calculate_hr(ibi) if len(ibi) > 0 else [])
        df['Predicted_HR_List_RF'] = df['Predicted_IBI_RF'].apply(lambda ibi: calculate_hr(ibi) if len(ibi) > 0 else [])

        # Get a single HR value (mean or median)
        df['Actual_HR'] = df['Actual_HR_List'].apply(get_single_hr_value)
        df['Predicted_HR_LSTM'] = df['Predicted_HR_List_LSTM'].apply(get_single_hr_value)
        df['Predicted_HR_RF'] = df['Predicted_HR_List_RF'].apply(get_single_hr_value)

        # Filter rows with NaN values in Predicted_HR columns and log skipped rows
        initial_count = len(df)
        df = df.dropna(subset=['Predicted_HR_LSTM', 'Predicted_HR_RF'])
        skipped_count = initial_count - len(df)
        if skipped_count > 0:
            logging.info(f"Skipped {skipped_count} rows with NaN values in Predicted HR columns.")

        # Filter out records with valid HR values for RMSE calculation
        valid_records = df.dropna(subset=['Actual_HR', 'Predicted_HR_LSTM', 'Predicted_HR_RF'])
        valid_hr_records_count = len(valid_records)

        # Calculate RMSE for LSTM and RF predictions
        rmse_lstm = math.sqrt(mean_squared_error(valid_records['Actual_HR'], valid_records['Predicted_HR_LSTM']))
        rmse_rf = math.sqrt(mean_squared_error(valid_records['Actual_HR'], valid_records['Predicted_HR_RF']))

        # Select relevant columns for response
        processed_data = df[['DeviceID', 'DateTime', 'IBI_values', 'Predicted_IBI_LSTM', 'Predicted_IBI_RF', 'Actual_HR', 'Predicted_HR_LSTM', 'Predicted_HR_RF']].to_dict(orient='records')

        # Convert to serializable structure
        serialized_data = make_serializable(processed_data)

        return {
            "status": "success",
            "processed_data": serialized_data,
            "overall_rmse": {
                "LSTM": rmse_lstm,
                "RF": rmse_rf
            },
            "valid_hr_records_count": valid_hr_records_count
        }

    except Exception as e:
        logging.error(f"Error during processing: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")