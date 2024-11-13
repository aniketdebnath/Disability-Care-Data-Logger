import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# Set the directory to save models and scalers
model_dir = r'A:\AnomalyDetection\mit-bih-project2\models'
os.makedirs(model_dir, exist_ok=True)

# Load the processed data
data_path = r'A:\AnomalyDetection\mit-bih-project2\data\processed\new_combined_beat_data.csv'
df = pd.read_csv(data_path)

# Drop rows with missing values (NaN)
df.dropna(inplace=True)

# Add a new feature combining RR Interval and Heart Rate as 'Intensity'
df['Intensity'] = df['RR_Interval'] * df['HeartRate']

# Define features (X) and labels (y)
features = ['RR_Interval', 'HeartRate', 'SDNN', 'SDSD', 'Intensity']
X = df[features]
y = df['Label']  # 1 for abnormal, 0 for normal

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Save the scaler
scaler_path = os.path.join(model_dir, 'xgb_scaler.pkl')
joblib.dump(scaler, scaler_path)
print(f"Scaler saved to {scaler_path}")

# Initialize XGBoost with scale_pos_weight to handle class imbalance
xgb_model = XGBClassifier(
    use_label_encoder=False,
    eval_metric='logloss',
    scale_pos_weight=len(y[y == 0]) / len(y[y == 1]),  # Balancing abnormal class
    random_state=42
)

# Train the model
xgb_model.fit(X_train, y_train)

# Save the trained model
model_path = os.path.join(model_dir, 'xgb_model_joblib.pkl')
joblib.dump(xgb_model, model_path)
print(f"Model saved to {model_path}")

# Cross-validation
cv_scores = cross_val_score(xgb_model, X_train, y_train, cv=5)
print(f"Cross-validation scores: {cv_scores}")
print(f"Mean cross-validation score: {np.mean(cv_scores)}")

# Evaluate the model on the test set
y_pred = xgb_model.predict(X_test)
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nAccuracy:", accuracy_score(y_test, y_pred))

# Trial Prediction Section
loaded_scaler = joblib.load(scaler_path)
loaded_model = joblib.load(model_path)

# Define a sample data point for prediction
sample_data = {
    'RR_Interval': 0.8,      # Example RR interval
    'HeartRate': 130,        # Example Heart rate
    'SDNN': 0.05,
    'SDSD': 0.03,
    'Intensity': 0.8 * 130   # Consistent with the Intensity feature
}

# Prepare sample data for prediction
sample_features = np.array([sample_data[feature] for feature in features]).reshape(1, -1)
sample_scaled = loaded_scaler.transform(sample_features)

# Make the prediction
sample_prediction = loaded_model.predict(sample_scaled)
sample_prediction_label = 'Abnormal' if sample_prediction[0] == 1 else 'Normal'

print(f"\nPrediction for sample data: {sample_prediction_label}")
