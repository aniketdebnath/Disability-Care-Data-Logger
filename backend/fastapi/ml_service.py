import os
import joblib
import pandas as pd
import numpy as np

# Load pre-trained models and scalers

svm_model = joblib.load('models/svm_model_joblib.pkl')
rf_model = joblib.load('models/rf_model_joblib.pkl')
knn_model = joblib.load('models/knn_model_joblib.pkl')
xgb_model = joblib.load('models/xgb_model_joblib.pkl')

# Load scalers
svm_scaler = joblib.load('models/svm_scaler.pkl')
rf_scaler = joblib.load('models/rf_scaler.pkl')
knn_scaler = joblib.load('models/knn_scaler.pkl')
xgb_scaler = joblib.load('models/xgb_scaler.pkl')

def process_signal(rr_interval, heart_rate, sdnn, sdsd):
    # Input data for models (without `Intensity`)
    input_data = pd.DataFrame([{
        'RR_Interval': rr_interval,
        'HeartRate': heart_rate,
        'SDNN': sdnn,
        'SDSD': sdsd
    }], columns=['RR_Interval', 'HeartRate', 'SDNN', 'SDSD'])
    
    # Add 'Intensity' for XGBoost model only
    xgb_input_data = input_data.copy()
    xgb_input_data['Intensity'] = rr_interval * heart_rate

    # Scale the input for each model
    svm_input_scaled = svm_scaler.transform(input_data)
    rf_input_scaled = rf_scaler.transform(input_data)
    knn_input_scaled = knn_scaler.transform(input_data)
    xgb_input_scaled = xgb_scaler.transform(xgb_input_data)

    # Debugging: Print scaled values for each model
    print("DEBUG: Scaled input values (SVM):", svm_input_scaled)
    print("DEBUG: Scaled input values (RF):", rf_input_scaled)
    print("DEBUG: Scaled input values (KNN):", knn_input_scaled)
    print("DEBUG: Scaled input values (XGBoost):", xgb_input_scaled)

    # Predictions and confidence scores
    svm_margin = float(svm_model.decision_function(svm_input_scaled)[0])
    rf_probabilities = rf_model.predict_proba(rf_input_scaled)[0]
    knn_probabilities = knn_model.predict_proba(knn_input_scaled)[0]
    xgb_probabilities = xgb_model.predict_proba(xgb_input_scaled)[0]

    # Debugging: Print SVM margin (confidence score)
    print("DEBUG: SVM confidence score (margin):", svm_margin)

    # Model predictions
    svm_prediction = int(svm_model.predict(svm_input_scaled)[0])
    rf_prediction = int(rf_model.predict(rf_input_scaled)[0])
    knn_prediction = int(knn_model.predict(knn_input_scaled)[0])
    xgb_prediction = int(xgb_model.predict(xgb_input_scaled)[0])

    # Confidence scores and reliability score
    rf_confidence = float(max(rf_probabilities))
    knn_confidence = float(max(knn_probabilities))
    xgb_confidence = float(max(xgb_probabilities))
    reliability_score = float(np.mean([abs(svm_margin), rf_confidence, knn_confidence, xgb_confidence]))

    # Debugging: Print reliability score
    print("DEBUG: Reliability score:", reliability_score)

    # Feature importance (only for RF and XGBoost)
    rf_feature_importance = {k: float(v) for k, v in zip(['RR_Interval', 'HeartRate', 'SDNN', 'SDSD'], rf_model.feature_importances_)}
    xgb_feature_importance = {k: float(v) for k, v in zip(['RR_Interval', 'HeartRate', 'SDNN', 'SDSD', 'Intensity'], xgb_model.feature_importances_)}

    # Combined prediction
    predictions = [svm_prediction, rf_prediction, knn_prediction, xgb_prediction]
    combined_prediction = 1 if predictions.count(1) > predictions.count(0) else 0

    # Plain language summary for UI display
    summary = "Abnormal" if combined_prediction == 1 else "Normal"
    explanation = (
        f"The signal was classified as '{summary}' based on an ensemble of models. "
        "Higher confidence levels indicate a stronger certainty in the abnormality detection. "
        "Feature importance provides insights into which features were most influential."
    )

    # UI-friendly output
    return {
        'combined_prediction': summary,
        'reliability_score': f"{reliability_score:.2f} (higher values indicate stronger confidence)",
        'model_predictions': {
            'svm_prediction': 'Abnormal' if svm_prediction == 1 else 'Normal',
            'svm_confidence': abs(svm_margin),
            'rf_prediction': 'Abnormal' if rf_prediction == 1 else 'Normal',
            'rf_confidence': rf_confidence,
            'rf_feature_importance': rf_feature_importance,
            'knn_prediction': 'Abnormal' if knn_prediction == 1 else 'Normal',
            'knn_confidence': knn_confidence,
            'xgb_prediction': 'Abnormal' if xgb_prediction == 1 else 'Normal',
            'xgb_confidence': xgb_confidence,
            'xgb_feature_importance': xgb_feature_importance,
        },
        'explanation': explanation,
        'message': 'Prediction successful'
    }
