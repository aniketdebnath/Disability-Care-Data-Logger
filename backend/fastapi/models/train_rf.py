import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
import joblib  # For saving/loading model

# Load your processed ECG data
data_path = r'A:\AnomalyDetection\mit-bih-project\data\processed\combined_beat_data.csv'
df = pd.read_csv(data_path)

# Optional: Drop any rows with missing values (NaN)
df.dropna(inplace=True)

# Define features (X) and labels (y)
X = df[['RR_Interval', 'HeartRate', 'QRS_Duration', 'P_Wave_Duration', 'QT_Interval']]
y = df['Label']  # 1 for abnormal, 0 for normal

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling: Normalize the features for better performance
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train a Random Forest classifier with hyperparameters
rf_model = RandomForestClassifier(
    n_estimators=100,          # Number of trees in the forest
    max_depth=None,             # Maximum depth of each tree (adjustable)
    min_samples_split=5,     # Minimum number of samples required to split an internal node
    min_samples_leaf=1,       # Minimum number of samples required to be at a leaf node
    class_weight='balanced',  # Handle imbalanced data
    random_state=42           # For reproducibility
)
rf_model.fit(X_train, y_train)

joblib.dump(scaler, 'rf_scaler.pkl')  # Save the scaler

# Save the trained model using joblib
joblib.dump(rf_model, 'rf_model_joblib.pkl')
print("Model saved to rf_model_joblib.pkl")

# Load the saved model
loaded_rf_model = joblib.load('rf_model_joblib.pkl')
print("Model loaded from rf_model_joblib.pkl")

# Predict on the test set
y_pred = loaded_rf_model.predict(X_test)

# Evaluate the model
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nAccuracy:", accuracy_score(y_test, y_pred))

# Incoming data should match the features used during training
incoming_data = pd.DataFrame({
    'RR_Interval': [0.7],  # Example values
    'HeartRate': [106],
    'QRS_Duration': [0.14],
    'P_Wave_Duration': [0.03],
    'QT_Interval': [0.35]
})
incoming_data_scaled = scaler.transform(incoming_data)  # Apply the same scaling
prediction = rf_model.predict(incoming_data_scaled)
print(f"Prediction for incoming data: {prediction}")

# Define parameter grid for GridSearchCV
param_grid = {
    'n_estimators': [50, 80, 100],  # Number of trees
    'max_depth': [None, 10, 20],    # Maximum depth of trees
    'min_samples_split': [2, 5],     # Minimum samples required to split an internal node
    'min_samples_leaf': [1, 2, 4],   # Minimum samples required at each leaf node
    'class_weight': ['balanced', None]  # Handle class imbalance
}

# # Step 1: Hyperparameter Tuning
# # Initialize GridSearchCV with RandomForestClassifier
# grid = GridSearchCV(RandomForestClassifier(), param_grid, cv=5, verbose=2, n_jobs=-1)

# # Fit GridSearchCV
# grid.fit(X_train, y_train)

# # Get the best parameters
# print("Best parameters found by GridSearchCV:", grid.best_params_)

# # Predict with the best estimator
# y_pred_grid = grid.best_estimator_.predict(X_test)

# # Evaluate the tuned model
# print("\nConfusion Matrix (GridSearchCV Model):")
# print(confusion_matrix(y_test, y_pred_grid))

# print("\nClassification Report (GridSearchCV Model):")
# print(classification_report(y_test, y_pred_grid))

# print("\nAccuracy (GridSearchCV Model):", accuracy_score(y_test, y_pred_grid))