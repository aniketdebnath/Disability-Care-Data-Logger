# fastapi_app/process_service.py
import math
import heartpy as hp
import numpy as np
from scipy.signal import butter, filtfilt

def bandpass_filter(data, lowcut, highcut, sample_rate, order=2):
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def process_ppg_signal(green_led_data_str):
    try:
        # Convert string of values to a list of integers
        green_led_data = [int(x) for x in green_led_data_str.split(',')]

        # Convert to numpy array and ensure enough data points
        green_led_data = np.array(green_led_data)
        # if len(green_led_data) < 100:
        #     raise ValueError("Not enough data points for heart rate analysis")

        # Apply bandpass filter to clean up noise
        filtered_data = bandpass_filter(green_led_data, lowcut=0.5, highcut=4, sample_rate=9)

        # Process data using heartpy with adjusted bpm constraints
        working_data, measures = hp.process(filtered_data, sample_rate=9, bpmmin=40, bpmmax=180)

        # Extract the heart rate and other metrics
        bpm = measures.get('bpm')
        ibi = measures.get('ibi')

        # Calculate RR Interval from IBI (IBI is in milliseconds)
        rr_interval = ibi / 1000.0 if ibi is not None else None  # Convert IBI to seconds
        
        # Check if bpm or rr_interval is NaN or infinite, replace with None if invalid
        if math.isnan(bpm) or math.isinf(bpm):
            bpm = None
        if rr_interval is not None and (math.isnan(rr_interval) or math.isinf(rr_interval)):
            rr_interval = None

        return rr_interval, bpm

    except Exception as e:
        raise ValueError(f"Error processing PPG signal: {e}")
