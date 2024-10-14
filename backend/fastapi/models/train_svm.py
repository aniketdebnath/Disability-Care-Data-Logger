import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.model_selection import GridSearchCV
import joblib

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

# Feature Scaling: Normalize the features for better performance of SVM
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train an SVM classifier
svm_model = SVC(kernel='rbf', C=10, gamma=1, class_weight='balanced')  # Radial basis function kernel
svm_model.fit(X_train, y_train)

# Predict on the test set
y_pred = svm_model.predict(X_test)

# Evaluate the model
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nAccuracy:", accuracy_score(y_test, y_pred))

joblib.dump(scaler, 'svm_scaler.pkl')  # Save the scaler

# Save the trained SVM model to a .pkl file using joblib
joblib.dump(svm_model, 'svm_model_joblib.pkl')
print("Model saved to svm_model_joblib.pkl")

# Step 1: Cross-Fold Validation
# skf = StratifiedKFold(n_splits=5)
# scores = cross_val_score(svm_model, X_train, y_train, cv=skf, scoring='accuracy')
# print("Cross-validated scores:", scores)

# Step 2: Grid Search for Hyperparameter Tuning
# perform_grid_search = input("\nDo you want to perform GridSearchCV for hyperparameter tuning? (yes/no): ").lower()

# if perform_grid_search == 'yes':
#     print("\nPerforming GridSearchCV for hyperparameter tuning...")
    
#     # Define parameter grid for GridSearchCV
#     param_grid = {
#         'C': [0.1, 1, 10],
#         'gamma': ['scale', 'auto', 0.1, 1],
#         'kernel': ['rbf']  # Using RBF kernel for SVM
#     }
    
#     # Initialize GridSearchCV with 5-fold cross-validation (you can change `cv` value)
#     grid = GridSearchCV(SVC(class_weight='balanced'), param_grid, refit=True, cv=2, verbose=2)

#     # Perform grid search on the training data
#     grid.fit(X_train, y_train)

#     # Get the best hyperparameters
#     print("Best parameters found by GridSearchCV:", grid.best_params_)

#     # Evaluate the grid search model on the test set
#     y_pred_grid = grid.best_estimator_.predict(X_test)

#     # Evaluate the grid search model
#     print("\nConfusion Matrix (GridSearchCV Model):")
#     print(confusion_matrix(y_test, y_pred_grid))

#     print("\nClassification Report (GridSearchCV Model):")
#     print(classification_report(y_test, y_pred_grid))

#     print("\nAccuracy (GridSearchCV Model):", accuracy_score(y_test, y_pred_grid))

# else:
#     print("Skipping GridSearchCV...")

# Best parameters found by GridSearchCV: {'C': 10, 'gamma': 1, 'kernel': 'rbf'}