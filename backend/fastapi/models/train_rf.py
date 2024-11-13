import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib  # For saving/loading model

# Set the directory to save models and scalers
model_dir = r'A:\AnomalyDetection\mit-bih-project2\models'
os.makedirs(model_dir, exist_ok=True)

# Load your processed data
data_path = r'A:\AnomalyDetection\mit-bih-project2\data\processed\new_combined_beat_data.csv'
df = pd.read_csv(data_path)

# Drop rows with missing values (NaN)
df.dropna(inplace=True)

# Define features (X) and labels (y) based on recent discussions
X = df[['RR_Interval', 'HeartRate', 'SDNN', 'SDSD']]
y = df['Label']  # 1 for abnormal, 0 for normal based on updated labels

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Save the scaler
scaler_path = os.path.join(model_dir, 'rf_scaler.pkl')
joblib.dump(scaler, scaler_path)
print(f"Scaler saved to {scaler_path}")

# Train a Random Forest classifier with specific hyperparameters
rf_model = RandomForestClassifier(
    n_estimators=100,          # Number of trees in the forest
    max_depth=None,            # Maximum depth of each tree
    min_samples_split=5,       # Minimum samples required to split an internal node
    min_samples_leaf=1,        # Minimum samples required at a leaf node
    class_weight='balanced',   # Handle imbalanced data
    random_state=42            # For reproducibility
)
rf_model.fit(X_train, y_train)

# Save the trained model
model_path = os.path.join(model_dir, 'rf_model_joblib.pkl')
joblib.dump(rf_model, 'rf_model_joblib.pkl')
print(f"Model saved to {model_path}")

# Evaluate with cross-validation
cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5)
print(f"Cross-validation scores: {cv_scores}")
print(f"Mean cross-validation score: {np.mean(cv_scores)}")

# Predict on the test set
y_pred = rf_model.predict(X_test)

# Evaluate the model
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nAccuracy:", accuracy_score(y_test, y_pred))

# --- Hyperparameter Tuning Section (Optional) ---

param_grid = {
    'n_estimators': [50, 100, 150],       # Number of trees
    'max_depth': [None, 10, 20],          # Maximum depth of trees
    'min_samples_split': [2, 5, 10],      # Minimum samples to split a node
    'min_samples_leaf': [1, 2, 4],        # Minimum samples at each leaf node
    'class_weight': ['balanced', None]    # Handle class imbalance
}

# # Uncomment this section to run GridSearchCV for hyperparameter tuning
# grid = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=5, verbose=2, n_jobs=-1)
# grid.fit(X_train, y_train)

# # Save the best model from GridSearchCV
# best_rf_model = grid.best_estimator_
# joblib.dump(best_rf_model, 'rf_model_best_joblib.pkl')
# print("Best model saved to rf_model_best_joblib.pkl")

# # Display best parameters found by GridSearchCV
# print("Best parameters found by GridSearchCV:", grid.best_params_)

# # Predict with the best estimator from GridSearchCV
# y_pred_grid = best_rf_model.predict(X_test)

# # Evaluate the tuned model
# print("\nConfusion Matrix (GridSearchCV Model):")
# print(confusion_matrix(y_test, y_pred_grid))

# print("\nClassification Report (GridSearchCV Model):")
# print(classification_report(y_test, y_pred_grid))

# print("\nAccuracy (GridSearchCV Model):", accuracy_score(y_test, y_pred_grid))

# --- Trial Prediction Section ---

# Load the scaler and model
loaded_scaler = joblib.load('rf_scaler.pkl')
loaded_model = joblib.load('rf_model_joblib.pkl')

# Define a sample data point for prediction
sample_data = {
    'RR_Interval': 0.7,     # Example value
    'HeartRate': 100,        # Example value
    'SDNN': 0.05,           # Example value
    'SDSD': 0.06            # Example value
}

# Ensure the sample data has only the features used in training
sample_features = [sample_data[feature] for feature in X.columns if feature in sample_data]
sample_features = np.array(sample_features).reshape(1, -1)

# Scale the sample data
sample_scaled = loaded_scaler.transform(sample_features)

# Make prediction
sample_prediction = loaded_model.predict(sample_scaled)
sample_prediction_label = 'Abnormal' if sample_prediction[0] == 1 else 'Normal'

print(f"\nPrediction for sample data: {sample_prediction_label}")
