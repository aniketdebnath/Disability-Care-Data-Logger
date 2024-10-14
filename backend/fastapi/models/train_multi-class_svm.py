import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# Load your processed ECG data
data_path = r'A:\AnomalyDetection\mit_bih_project\data\processed\combined_beat_data.csv'
df = pd.read_csv(data_path)

# Optional: Drop any rows with missing values (NaN)
df.dropna(inplace=True)

# Keep only relevant symbols for training
relevant_symbols = ['V', '[', '!', ']', 'L', 'R', 'N']  # Include 'N' for normal if needed
df_filtered = df[df['Symbol'].isin(relevant_symbols)].copy()

# Replace symbols with integers for multi-class classification
df_filtered.loc[:, 'Symbol'] = df_filtered['Symbol'].replace({
    'N': 0,  # Normal
    'V': 1,
    '[': 2,
    '!': 3,
    ']': 4,
    'L': 5,
    'R': 6
})

# Convert the Symbol column to a numeric type
df_filtered['Symbol'] = pd.to_numeric(df_filtered['Symbol'], errors='coerce')

# Check the unique labels and data type
print("Unique labels in 'Symbol':", df_filtered['Symbol'].unique())
print("Data type of y:", df_filtered['Symbol'].dtype)

# Define features (X) and labels (y)
X = df_filtered[['RR_Interval', 'HeartRate', 'QRS_Duration', 'P_Wave_Duration', 'QT_Interval']]
y = df_filtered['Symbol']  # Multi-class labels

# Ensure that y is not empty
if y.isnull().any():
    print("There are NaN values in 'Symbol' after conversion. Please check the data.")
    y = y.dropna()  # Drop NaN values if they exist

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling: Normalize the features for better performance of SVM
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train a One-vs-Rest SVM classifier for multi-class classification
svm_model = SVC(kernel='rbf', C=10, gamma=1, class_weight='balanced')
svm_model.fit(X_train, y_train)

# Save the trained SVM model to a .pkl file using joblib
joblib.dump(svm_model, 'multi_class_svm_model_joblib.pkl')
print("Multi-class SVM model saved to multi_class_svm_model_joblib.pkl")

# Predict on the test set
y_pred = svm_model.predict(X_test)

# Evaluate the model
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nAccuracy:", accuracy_score(y_test, y_pred))
