ECG Abnormality Detection Using Random Forest Classifier

This project focuses on detecting cardiac arrhythmias and abnormalities in ECG signals using a Random Forest Classifier. The dataset includes key features like RR intervals, heart rate, QRS duration, P-wave duration, and QT interval, which are essential for detecting conditions such as Premature Ventricular Contractions (PVC), Bundle Branch Blocks (LBBB, RBBB), and Ventricular Fibrillation. The Random Forest model is fine-tuned using hyperparameter optimization and class balancing to improve the detection of abnormal heartbeats.

Why Use a Random Forest Classifier?

Random Forest Classifiers are particularly effective for high-dimensional datasets like ECG signals due to their ability to reduce overfitting and handle noisy data. By combining the predictions of multiple decision trees, Random Forests can make more robust classifications. Additionally, they provide insights into feature importance, allowing for better understanding and selection of the most relevant features for detecting abnormalities.

In this section, we use a Random Forest Classifier with specific hyperparameters optimized for the ECG dataset.
1. Random Forest Classifier

The Random Forest model is configured with the following hyperparameters:

python

rf_model = RandomForestClassifier(
    n_estimators=80,          # Number of trees in the forest
    max_depth=None,           # Unlimited depth, allowing trees to grow to their maximum
    min_samples_split=10,     # Minimum samples required to split an internal node
    min_samples_leaf=5,       # Minimum samples required at a leaf node
    class_weight='balanced',   # Adjusts weights inversely proportional to class frequencies
    random_state=42           # For reproducibility
)

Explanation of Hyperparameters:

    n_estimators: The number of trees in the forest. After experimentation, we set this to 80, which resulted in optimal performance.

    max_depth: This parameter controls the maximum depth of each tree. Setting it to None allows trees to grow to their maximum depth, which is helpful for capturing the complexities in the data.

    min_samples_split: This parameter determines the minimum number of samples required to split an internal node. A value of 10 helps prevent overfitting by ensuring nodes have sufficient samples before splitting.

    min_samples_leaf: This specifies the minimum number of samples required at a leaf node. A value of 5 prevents the model from creating very small leaf nodes, which can lead to overfitting.

    class_weight: Setting this to 'balanced' adjusts the weights for the classes, ensuring that the model pays equal attention to minority (abnormal) and majority (normal) classes.

2. Hyperparameter Tuning

To further enhance model performance, we utilize GridSearchCV for hyperparameter tuning. This technique evaluates multiple combinations of hyperparameters to identify the best performing model configuration.

python

param_grid = {
    'n_estimators': [50, 80, 100],  # Number of trees
    'max_depth': [None, 10, 20],     # Depth of trees
    'min_samples_split': [2, 5, 10], # Minimum samples to split
    'min_samples_leaf': [1, 5, 10],  # Minimum samples at leaf node
    'class_weight': ['balanced']      # Class weighting
}

grid = GridSearchCV(RandomForestClassifier(), param_grid, refit=True, cv=5)
grid.fit(X_train, y_train)

print("Best parameters found: ", grid.best_params_)

Results After Hyperparameter Tuning:

The best parameters found were:

csharp

Best parameters found by GridSearchCV: {'class_weight': 'balanced', 'max_depth': None, 'min_samples_leaf': 1, 'min_samples_split': 5, 'n_estimators': 100}

    Confusion Matrix (GridSearchCV Model):

[[15081   126]
 [  227  6518]]

    Classification Report (GridSearchCV Model):

markdown

              precision    recall  f1-score   support
         0.0       0.99      0.99      0.99     15207
         1.0       0.98      0.97      0.97      6745

    Accuracy (GridSearchCV Model): 0.9839

4. Evaluation

After training the model, we evaluate its performance using a confusion matrix and classification report to assess precision, recall, and F1-score.

    Confusion Matrix:

[[15045   162]
 [  279  6466]]

    Classification Report:

              precision    recall  f1-score   support
         0.0       0.98      0.99      0.99     15207
         1.0       0.98      0.96      0.97      6745

    Accuracy: 0.9799

Conclusion

The Random Forest Classifier effectively detects arrhythmias in ECG data. Key techniques such as hyperparameter tuning through GridSearchCV and class balancing have significantly improved model performance. The combination of these methodologies allows for accurate detection of cardiac abnormalities, enhancing diagnostic capabilities in clinical settings.
Summary of Techniques Used:

    Random Forest Classifier: An ensemble method that reduces overfitting while improving accuracy.
    Hyperparameter Tuning: Optimizes the model's performance by testing different configurations.
    Class Balancing: Ensures that the model adequately represents both normal and abnormal classes, preventing bias toward the majority class (normal beats).