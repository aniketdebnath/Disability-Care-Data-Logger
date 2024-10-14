import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
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

# Train a KNN classifier with a default number of neighbors
knn_model = KNeighborsClassifier(n_neighbors=11, weights='distance', metric='manhattan')  # Initial configuration
knn_model.fit(X_train, y_train)

joblib.dump(scaler, 'knn_scaler.pkl')  # Save the scaler

# Save the trained model using joblib
joblib.dump(knn_model, 'knn_model_joblib.pkl')
print("Model saved to knn_model_joblib.pkl")

# Load the saved model
loaded_knn_model = joblib.load('knn_model_joblib.pkl')
print("Model loaded from knn_model_joblib.pkl")

# Predict on the test set
y_pred = loaded_knn_model.predict(X_test)

# Evaluate the model
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nAccuracy:", accuracy_score(y_test, y_pred))

# # Step 2: Hyperparameter Tuning
# # Define parameter grid for GridSearchCV
# param_grid = {
#     'n_neighbors': [1, 3, 5, 7, 9, 11],  # Testing odd numbers for k to avoid ties
#     'weights': ['uniform', 'distance'],  # Uniform weights or distance-based weights
#     'metric': ['euclidean', 'manhattan']  # Distance metrics
# }

# # Initialize GridSearchCV with KNeighborsClassifier
# grid = GridSearchCV(KNeighborsClassifier(), param_grid, cv=5, verbose=2)

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
