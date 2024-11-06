import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks
from pymongo import MongoClient
from tensorflow.keras.models import load_model
import joblib
from fastapi import FastAPI, HTTPException
import json
from bson import json_util

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

def process_mpu6050_data(mpu_data: str):
    """ Convert the MPU6050 data from string to a list of floats """
    return [float(i) for i in mpu_data.split(',')]

# Function to convert non-serializable types like int64
def convert_data_for_serialization(data):
    """ Convert data types to JSON-serializable types """
    if isinstance(data, (np.int64, np.int32)):
        return int(data)
    if isinstance(data, np.ndarray):
        return data.tolist()  # Convert NumPy arrays to lists
    if isinstance(data, pd.Timestamp):
        return str(data)  # Convert Timestamp to string
    return data

# Recursive function to convert entire structure to serializable types
def make_serializable(data):
    if isinstance(data, dict):
        return {k: make_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_serializable(item) for item in data]
    else:
        return convert_data_for_serialization(data)

# Step 7: Load the LSTM model and scaler
model = load_model('models/lstm_model_ms_seq_10.h5')
scaler = joblib.load('models/scaler_ms_seq_10.pkl')

# Step 8: Predict IBI values using the LSTM model
def predict_lstm(ibi_values, sequence_length=10):
    ibi_values = np.array(ibi_values).reshape(-1, 1)  # Reshape to (n_samples, 1)
    
    # Scale the IBI values
    ibi_scaled = scaler.transform(ibi_values)
    
    # Prepare sequences for LSTM
    X_sequences = prepare_lstm_data(ibi_scaled, sequence_length=sequence_length)
    
    # Check if there are enough sequences
    if X_sequences.size == 0:
        return np.array([])  # Return empty array if no sequences are available
    
    # Predict using the LSTM model
    y_pred_scaled = model.predict(X_sequences)
    
    # Rescale predictions back to original scale
    y_pred = scaler.inverse_transform(y_pred_scaled).flatten()
    
    return y_pred

# Step 9: Calculate Heart Rate from IBI values
def calculate_hr(ibi_values):
    ibi_values = np.array(ibi_values)
    hr = 60000 / ibi_values  # HR in BPM
    return hr

# Step 6: Prepare IBI sequences for LSTM model input
def prepare_lstm_data(ibi_values, sequence_length=10):
    sequences = []
    for i in range(len(ibi_values) - sequence_length):
        sequences.append(ibi_values[i:i + sequence_length])
    return np.array(sequences)

# Helper function to get a single HR value (mean or median)
def get_single_hr_value(hr_values):
    if len(hr_values) > 0:
        return np.mean(hr_values)  # You can change this to np.median(hr_values) if needed
    return None

# Main route to process MongoDB data, calculate IBI values, and make predictions
@app.get("/process-mongodb-data")
def process_mongodb_data():
    try:
        # Retrieve data from MongoDB
        data_cursor = collection.find({})
        data_list = list(data_cursor)

        if not data_list:
            raise HTTPException(status_code=404, detail="No data found in MongoDB")

        # Convert MongoDB data to pandas DataFrame
        df = pd.DataFrame(data_list)

        # Process each LED data column (GreenLED, IRLED, RedLED) and MPU6050 data
        df['GreenLED_processed'] = df['GreenLED'].apply(process_led_data)
        df['IRLED_processed'] = df['IRLED'].apply(process_led_data)
        df['RedLED_processed'] = df['RedLED'].apply(process_led_data)
        df['MPU6050_processed'] = df['MPU6050'].apply(process_mpu6050_data)

        # Process IR LED signal and calculate IBI values
        df['IBI_values'] = df['IRLED_processed'].apply(lambda ir_led: process_ir_led_signal(ir_led, sample_rate=125))

        # Predict IBI values using LSTM
        df['Predicted_IBI'] = df['IBI_values'].apply(lambda ibi: predict_lstm(ibi, sequence_length=10) if len(ibi) >= 10 else [])

        # Calculate HR values from actual and predicted IBI values
        df['Actual_HR_List'] = df['IBI_values'].apply(lambda ibi: calculate_hr(ibi) if len(ibi) > 0 else [])
        df['Predicted_HR_List'] = df['Predicted_IBI'].apply(lambda ibi: calculate_hr(ibi) if len(ibi) > 0 else [])

        # Get a single actual HR and predicted HR by averaging or taking the median
        df['Actual_HR'] = df['Actual_HR_List'].apply(get_single_hr_value)
        df['Predicted_HR'] = df['Predicted_HR_List'].apply(get_single_hr_value)

        # Select relevant columns for response
        processed_data = df[['DeviceID', 'DateTime', 'IBI_values', 'Predicted_IBI', 'Actual_HR', 'Predicted_HR']].to_dict(orient='records')

        # Convert to serializable structure
        serialized_data = make_serializable(processed_data)

        return {"status": "success", "processed_data": serialized_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
