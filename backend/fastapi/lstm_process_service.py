import numpy as np
from scipy.signal import butter, filtfilt

def bandpass_filter(data, lowcut, highcut, sample_rate, order=2):
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def process_bvp_signal(ir_led_data_str, sequence_length=100):
    try:
        # Convert the incoming IR LED data into a list of integers
        ir_led_data = np.array([int(x) for x in ir_led_data_str.split(',') if x.isdigit()], dtype=np.int32)

        # Apply bandpass filter to clean the signal
        filtered_data = bandpass_filter(ir_led_data, lowcut=0.67, highcut=3, sample_rate=125)
        
        # Check filtered data shape
        print("Filtered Data Shape:", filtered_data.shape)

        # Prepare LSTM-compatible sequences
        sequences = []
        for i in range(0, len(filtered_data) - sequence_length, sequence_length):
            sequence = filtered_data[i:i + sequence_length]
            sequences.append(sequence)
        
        sequences_array = np.array(sequences).reshape(-1, sequence_length, 1)
        
        # Check sequences shape
        print("Sequences Shape for LSTM:", sequences_array.shape)
        
        return sequences_array  # Shape: (num_sequences, sequence_length, 1)
    except Exception as e:
        raise ValueError(f"Error in processing BVP for LSTM: {e}")
