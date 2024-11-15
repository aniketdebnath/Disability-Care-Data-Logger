
import numpy as np
import logging
import joblib
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
import pymongo
from utils.helpers import bandpass_filter, read_entries_for_tuning, is_pulse_present, clamp, update_tuning_data_in_mongodb, is_improving

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Define the path to the model
model_path = os.path.join(os.path.dirname(__file__), "RandomForrestModelFirmWareAutoTune.pkl")

# Load the pre-trained model for evaluating signal quality
model = joblib.load(model_path)
# Main function for running the tuning cycle with quality checks
def run_tuning_cycle():
    baseline_median = None
    baseline_iqr = None
    best_median = -np.inf
    best_iqr = np.inf
    best_tuning = None

    entries = read_entries_for_tuning()

    if entries:
        for device_id, raw_data, date_time, document in entries:
            logging.info(f"Processing entry for DeviceID: {device_id} with timestamp: {date_time}")

            if is_pulse_present(raw_data):
                logging.info("Pulse detected.")

                current_led1 = document["TuningData"].get("LED1_CURRENT", 30)
                current_led3 = document["TuningData"].get("LED3_CURRENT", 30)
                current_gain_idx = document["TuningData"].get("GAIN", 0)
                current_tia_cf_idx = document["TuningData"].get("TIA_CF", 0)

                new_led1, new_led3, new_gain, new_tia_cf = adjust_tuning_parameters(
                    raw_data, current_led1, current_led3, current_gain_idx, current_tia_cf_idx)

                median_quality, iqr_quality = evaluate_signal_quality(model, raw_data)

                if baseline_median is None or baseline_iqr is None:
                    baseline_median, baseline_iqr = median_quality, iqr_quality

                if is_improving(median_quality, iqr_quality, baseline_median, baseline_iqr):
                    baseline_median, baseline_iqr = median_quality, iqr_quality
                    best_median, best_iqr = median_quality, iqr_quality
                    best_tuning = (new_led1, new_led3, new_gain, new_tia_cf)
                    logging.info(f"Improvement detected. Updated best tuning parameters.")

                if best_tuning and not is_improving(median_quality, iqr_quality, best_median, best_iqr):
                    logging.info(f"No further improvements detected. Applying best-found tuning parameters.")
                    new_led1, new_led3, new_gain, new_tia_cf = best_tuning
                    auto_tune_ideal = True
                else:
                    auto_tune_ideal = False

                date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                update_tuning_data_in_mongodb(device_id, date_time, new_led1, new_led3, new_gain, new_tia_cf, auto_tune_ideal, document)
            else:
                logging.warning(f"No pulse detected for DeviceID: {device_id}. Skipping evaluation.")
    else:
        logging.warning("No entries found for tuning.")
