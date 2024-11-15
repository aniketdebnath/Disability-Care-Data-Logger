
import pymongo
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
import logging

# MongoDB Configuration
mongo_uri = "mongodb+srv://FYPUSERS:k1iTgwyFFzGlAkeN@fyptestdb.d7zdlnq.mongodb.net/?authMechanism=DEFAULT"
database_name = "FYPData"
collection_name = "TuningInformation"

# Initialize MongoDB client
client = pymongo.MongoClient(mongo_uri)
db = client[database_name]
collection = db[collection_name]

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def bandpass_filter(signal, lowcut=0.5, highcut=3.5, fs=125, order=3):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

def read_entries_for_tuning():
    logging.debug("Querying MongoDB for entries with AutoTuneIdeal set to false and ESPUTD set to true...")
    query = {"AutoTuneIdeal": False, "ESPUTD": True}
    documents = collection.find(query)

    entries = []
    for document in documents:
        if "MostRecentReadings" in document:
            most_recent_readings = document["MostRecentReadings"]

            if "GreenLED" in most_recent_readings and "IRLED" in most_recent_readings and "DateTime" in most_recent_readings:
                green_led_values = most_recent_readings["GreenLED"]
                ir_led_values = most_recent_readings["IRLED"]
                date_time = most_recent_readings["DateTime"]

                if not green_led_values or not ir_led_values:
                    logging.warning(f"Skipping DeviceID: {document['DeviceID']} due to empty LED values.")
                    continue

                try:
                    green_led_values = list(map(int, green_led_values.split(",")))
                    ir_led_values = list(map(int, ir_led_values.split(",")))

                    raw_data = list(zip(green_led_values, ir_led_values))
                    entries.append((document["DeviceID"], raw_data, date_time, document))
                except ValueError as e:
                    logging.warning(f"ValueError while processing DeviceID: {document['DeviceID']}. Error: {e}")
            else:
                logging.warning(f"Missing MostRecentReadings or DateTime for DeviceID: {document['DeviceID']}")
    return entries

def is_pulse_present(data):
    green_led_data = bandpass_filter([item[0] for item in data])
    ir_led_data = bandpass_filter([item[1] for item in data])

    threshold_green = np.mean(green_led_data) + 0.5 * np.std(green_led_data)
    threshold_ir = np.mean(ir_led_data) + 0.5 * np.std(ir_led_data)

    peaks_green, _ = find_peaks(green_led_data, height=threshold_green, distance=50, prominence=0.8)
    peaks_ir, _ = find_peaks(ir_led_data, height=threshold_ir, distance=50, prominence=0.8)

    return len(peaks_green) > 1 or len(peaks_ir) > 1

def update_tuning_data_in_mongodb(device_id, date_time, new_led1, new_led3, new_gain, new_tia_cf, auto_tune_ideal, document):
    logging.debug(f"Updating tuning data in MongoDB for {device_id}...")

    tuning_object = {
        "TuningData": {
            "LED1_CURRENT": new_led1,
            "LED3_CURRENT": new_led3,
            "GAIN": new_gain,
            "TIA_CF": new_tia_cf,
            "DateTime": date_time
        },
        "AutoTuneIdeal": auto_tune_ideal,
        "ESPUTD": False
    }

    query = {"DeviceID": device_id}
    collection.update_one(query, {"$set": tuning_object})
    logging.info(f"Tuning data updated in MongoDB for DeviceID: {device_id}")

def is_improving(median_quality, iqr_quality, baseline_median, baseline_iqr, tolerance=0.05):
    median_improvement = (median_quality - baseline_median) / baseline_median > tolerance
    iqr_reduction = (baseline_iqr - iqr_quality) / baseline_i
