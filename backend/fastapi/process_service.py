import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
import math

# Step 1: Bandpass filter for noise reduction
def bandpass_filter(data, lowcut, highcut, sample_rate, order=2):
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

# Step 2: Detect peaks in the PPG signal
def detect_peaks(filtered_data, sample_rate):
    min_distance = sample_rate * 0.5  # 0.5s for 120 bpm
    peaks, _ = find_peaks(filtered_data, distance=min_distance)
    return peaks

# Step 3: Calculate IBI (Inter-Beat Interval) from peaks
def calculate_ibi(peaks, sample_rate):
    if len(peaks) > 1:
        ibi_intervals = np.diff(peaks) / sample_rate * 1000  # Convert to milliseconds
        return ibi_intervals
    else:
        return np.array([])

# Step 4: Calculate heart rate metrics (RR Interval, HeartRate, SDNN, SDSD)
def calculate_heart_rate_metrics(ibi_intervals):
    if len(ibi_intervals) > 0:
        heart_rates = 60000 / ibi_intervals  # Heart rate in BPM
        rr_interval = np.mean(ibi_intervals) / 1000  # Average RR interval in seconds
        sdnn = np.std(ibi_intervals)  # Standard deviation of NN intervals
        sdsd = np.std(np.diff(ibi_intervals))  # SDSD: Standard deviation of successive differences
        return rr_interval, np.mean(heart_rates), sdnn, sdsd
    else:
        return None, None, None, None

# Main function to process a PPG signal and return features
def process_ppg_signal(ir_led_data_str):
    try:
        # Convert string of values to a list of integers
        ir_led_data = [int(x) for x in ir_led_data_str.split(',') if x.isdigit()]

        # Convert to numpy array and check minimum data length
        ir_led_data = np.array(ir_led_data)
        if len(ir_led_data) < 125:  # Minimum 1-second worth of data at 125Hz
            raise ValueError("Not enough data points for heart rate analysis")

        # Step 1: Apply bandpass filter to reduce noise
        filtered_data = bandpass_filter(ir_led_data, lowcut=0.67, highcut=3, sample_rate=125)

        # Step 2: Detect peaks in the filtered data
        peaks = detect_peaks(filtered_data, sample_rate=125)

        # Step 3: Calculate IBI (Inter-Beat Interval) values
        ibi_intervals = calculate_ibi(peaks, sample_rate=125)

        # Step 4: Calculate heart rate, RR interval, SDNN, and SDSD
        rr_interval, heart_rate, sdnn, sdsd = calculate_heart_rate_metrics(ibi_intervals)

        # Validate the results and ensure there are no NaN or infinite values
        if math.isnan(heart_rate) or math.isinf(heart_rate):
            heart_rate = None
        if rr_interval is not None and (math.isnan(rr_interval) or math.isinf(rr_interval)):
            rr_interval = None
        if sdnn is not None and (math.isnan(sdnn) or math.isinf(sdnn)):
            sdnn = None
        if sdsd is not None and (math.isnan(sdsd) or math.isinf(sdsd)):
            sdsd = None

        # Return the processed data without ibi
        return rr_interval, heart_rate, sdnn/1000, sdsd/1000

    except Exception as e:
        raise ValueError(f"Error processing PPG signal: {e}")
