import numpy as np
from tensorflow.keras.models import load_model

# Load the pre-trained LSTM model
MODEL_PATH = "models/lstm_model.keras"  # Replace with your actual path
lstm_model = load_model(MODEL_PATH)

def predict_lstm(data):
    """
    Make predictions using the loaded LSTM model.
    
    Parameters:
    - data: Preprocessed input data for LSTM, shape (num_sequences, sequence_length, 1).
    
    Returns:
    - A dictionary with 'lstm_prediction' as the majority prediction class (e.g., 'stress' or 'normal')
      and 'confidence_score' as the average confidence for the majority class.
    """
    try:
        # Get raw predictions (probabilities) from the model
        predictions = lstm_model.predict(data)  # Shape: (num_sequences, 1)
        print(f"Raw LSTM Predictions: {predictions}")

        # Threshold the predictions to binary classes (e.g., 0 or 1)
        predicted_classes = (predictions > 0.5).astype(int).flatten()
        print(f"Predicted Classes: {predicted_classes}")

        # Majority vote for final class (0 or 1) as the LSTM prediction
        majority_class = np.argmax(np.bincount(predicted_classes))

        # Calculate the confidence score as the average probability of the majority class
        confidence_score = np.mean(predictions[predicted_classes == majority_class])

        # Map classes to human-readable labels (optional)
        class_labels = {0: "normal", 1: "stress"}
        lstm_prediction = class_labels.get(majority_class, "Unknown")

        # Return the structured result
        return {
            "lstm_prediction": lstm_prediction,
            "confidence_score": confidence_score
        }
    except Exception as e:
        raise ValueError(f"Error in LSTM prediction: {e}")
