import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# Set the directory to save models and scalers
model_dir = r'A:\AnomalyDetection\mit-bih-project2\models'
os.makedirs(model_dir, exist_ok=True)

# Load your processed data
data_path = r'A:\AnomalyDetection\mit-bih-project2\data\processed\new_combined_beat_data.csv'
df = pd.read_csv(data_path)

# Drop rows with missing values (NaN)
df.dropna(inplace=True)

# Define features (X) and labels (y)
features = ['RR_Interval', 'HeartRate', 'SDNN', 'SDSD']
X = df[features]
y = df['Label']  # 1 for abnormal, 0 for normal

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling: Normalize the features for better performance of SVM
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Save the scaler
scaler_path = os.path.join(model_dir, 'svm_scaler.pkl')
joblib.dump(scaler, scaler_path)
print(f"Scaler saved to {scaler_path}")

# Train an SVM classifier with the best known parameters
svm_model = SVC(kernel='rbf', C=10, gamma=1, class_weight='balanced')
svm_model.fit(X_train, y_train)

# Save the trained SVM model
model_path = os.path.join(model_dir, 'svm_model_joblib.pkl')
joblib.dump(svm_model, model_path)
print(f"Model saved to {model_path}")

# Evaluate the model
y_pred = svm_model.predict(X_test)
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nAccuracy:", accuracy_score(y_test, y_pred))

# --- Sample Prediction Section ---

# Load scaler and model for sample prediction
loaded_scaler = joblib.load(scaler_path)
loaded_model = joblib.load(model_path)

# Define a sample data point with explicit column order
sample_data = pd.DataFrame([{
    'RR_Interval': 0.984,
    'HeartRate': 64.126,
    'SDNN': 181.66 / 1000,  # Adjust scaling if needed
    'SDSD': 199.54 / 1000   # Adjust scaling if needed
}], columns=features)  # Ensure correct column order

# Scale the sample data
sample_scaled = loaded_scaler.transform(sample_data)

# Predict
sample_prediction = loaded_model.predict(sample_scaled)
sample_prediction_label = 'Abnormal' if sample_prediction[0] == 1 else 'Normal'
print(f"\nPrediction for sample data: {sample_prediction_label}")
# Debugging the scaled input within the API or test
print("Scaled input values (SVM):", sample_scaled)

# Compare the SVM confidence score
svm_confidence_score = svm_model.decision_function(sample_scaled)
print("SVM confidence score:", svm_confidence_score)