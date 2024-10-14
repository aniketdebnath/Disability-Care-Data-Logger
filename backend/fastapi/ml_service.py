import joblib
import pandas as pd
import numpy as np

# Load the pre-trained models and their respective scalers
svm_model = joblib.load('../ppg-signal-processing/models/svm_model_joblib.pkl')
rf_model = joblib.load('../ppg-signal-processing/models/rf_model_joblib.pkl')
knn_model = joblib.load('../ppg-signal-processing/models/knn_model_joblib.pkl')

# Load the scalers
svm_scaler = joblib.load('../ppg-signal-processing/models/svm_scaler.pkl')
rf_scaler = joblib.load('../ppg-signal-processing/models/rf_scaler.pkl')
knn_scaler = joblib.load('../ppg-signal-processing/models/knn_scaler.pkl')

def process_signal(rr_interval, heart_rate):
    # Default values for missing features
    qrs_default = 0.14  
    qt_default = 0.35   
    p_wave_default = 0.04  

    # Create the input feature DataFrame with the appropriate feature names
    input_data = pd.DataFrame([{
        'RR_Interval': rr_interval,
        'HeartRate': heart_rate,
        'QRS_Duration': qrs_default,
        'P_Wave_Duration': p_wave_default,
        'QT_Interval': qt_default
    }])


    # Apply the correct scaler for each model
    svm_input_scaled = svm_scaler.transform(input_data)
    rf_input_scaled = rf_scaler.transform(input_data)
    knn_input_scaled = knn_scaler.transform(input_data)

    # Predictions with probabilities
    svm_margin = svm_model.decision_function(svm_input_scaled)[0]  # Confidence margin for SVM
    rf_probabilities = rf_model.predict_proba(rf_input_scaled)[0]  # RF probability
    knn_probabilities = knn_model.predict_proba(knn_input_scaled)[0]  # KNN probability

    # Predictions
    svm_prediction = svm_model.predict(svm_input_scaled)[0]
    rf_prediction = rf_model.predict(rf_input_scaled)[0]
    knn_prediction = knn_model.predict(knn_input_scaled)[0]

    # Confidence Scores
    rf_confidence = max(rf_probabilities)
    knn_confidence = max(knn_probabilities)

    # Feature Importance for RF
    rf_feature_importance = dict(zip(['RR_Interval', 'HeartRate', 'QRS_Duration', 'P_Wave_Duration', 'QT_Interval'], rf_model.feature_importances_))

    # Return detailed predictions
    return {
        'svm_prediction': svm_prediction,
        'svm_confidence': abs(svm_margin),  # Distance from decision boundary as confidence
        'rf_prediction': rf_prediction,
        'rf_confidence': rf_confidence,
        'rf_feature_importance': rf_feature_importance,
        'knn_prediction': knn_prediction,
        'knn_confidence': knn_confidence,
        'message': 'Prediction successful'
    }
