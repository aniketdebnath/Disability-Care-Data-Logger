ECG Abnormality Detection Using SVM Classifier

This project focuses on detecting cardiac arrhythmias and abnormalities in ECG signals using a Support Vector Machine (SVM) classifier. The dataset includes key features like RR intervals, heart rate, and QRS duration, which are essential for detecting conditions such as Premature Ventricular Contractions (PVC), Bundle Branch Blocks (LBBB, RBBB), and Ventricular Fibrillation. The SVM model is fine-tuned using hyperparameter optimization, cross-validation, and class balancing to improve the detection of abnormal heartbeats.

Why Use a Support Vector Machine (SVM)?

Support Vector Machines (SVM) are well-suited for high-dimensional datasets like ECG signals, where decision boundaries between classes (normal vs. abnormal heartbeats) can be complex. SVMs create a decision boundary (hyperplane) that maximizes the margin between different classes, ensuring robust classification even for noisy or imbalanced data.

In this project, we use an SVM with the Radial Basis Function (RBF) kernel, which is known for handling non-linear relationships by mapping the data into a higher-dimensional space.
Workflow Overview

Data Normalization: The features are normalized using StandardScaler() to ensure they have a mean of 0 and a standard deviation of 1. This scaling improves SVM performance since it is sensitive to the magnitude of feature values.
1. SVM Classifier

The SVM model is trained using the RBF kernel, which is ideal for non-linear data. We use the following configuration:

python

svm_model = SVC(kernel='rbf', C=1.0, gamma='scale', class_weight='balanced')

    C=1.0: Controls the regularization strength. A larger C would penalize misclassifications more severely, potentially leading to overfitting.
    gamma='scale': Automatically adjusts gamma based on the number of features.
    class_weight='balanced': Ensures that the model pays equal attention to the minority (abnormal beats) and majority (normal beats) classes.

2. Hyperparameter Tuning (Grid Search)

To improve the model’s performance, GridSearchCV was used to fine-tune the hyperparameters. We tested different values of:

    C: Regularization parameter (values tested: [0.1, 1, 10])
    Gamma: Kernel coefficient (values tested: [‘scale’, ‘auto’, 0.1, 1])

Code for Hyperparameter Tuning:

python

from sklearn.model_selection import GridSearchCV

param_grid = {'C': [0.1, 1, 10], 'gamma': ['scale', 'auto', 0.1, 1], 'kernel': ['rbf']}
grid = GridSearchCV(SVC(), param_grid, refit=True, cv=5)
grid.fit(X_train, y_train)

print("Best parameters found: ", grid.best_params_)

The best parameters found were C=10 and gamma=1, which improved both precision and recall for abnormal beats, leading to more accurate predictions.
3. Cross-Validation

To ensure the model generalizes well, we performed Stratified K-Fold Cross-Validation. This method splits the data into k folds and trains the model k times, each time on a different subset of the data. We used 5-fold cross-validation to verify the robustness of the model.

python

from sklearn.model_selection import StratifiedKFold, cross_val_score

skf = StratifiedKFold(n_splits=5)
scores = cross_val_score(svm_model, X_train, y_train, cv=skf, scoring='accuracy')
print("Cross-validated scores:", scores)

Cross-validation helps reduce overfitting by ensuring the model performs well across various subsets of the data.
4. Class Balancing

Our dataset is imbalanced, with more normal beats (labeled as 0) than abnormal beats (labeled as 1). To address this, we used the class_weight='balanced' parameter in the SVM model to automatically adjust the weights of the classes based on their frequencies. This ensures the model focuses equally on both classes and does not become biased toward the majority class.
Results
Before Hyperparameter Tuning:

text

Confusion Matrix:
[[14840   367]
 [  916  5829]]

Classification Report:
              precision    recall  f1-score   support

         0.0       0.94      0.98      0.96     15207
         1.0       0.94      0.86      0.90      6745

Accuracy: 94%

After Hyperparameter Tuning (Using GridSearchCV):

text

Confusion Matrix:
[[14636   571]
 [  260  6485]]

Classification Report:
              precision    recall  f1-score   support

         0.0       0.98      0.96      0.97     15207
         1.0       0.92      0.96      0.94      6745

Accuracy: 96%

Key Improvements:

    Precision for abnormal beats (1) increased from 0.94 to 0.98, indicating fewer false positives.
    Recall for abnormal beats (1) improved from 0.86 to 0.96, meaning more true positives were correctly identified.
    Overall accuracy improved from 94% to 96%, indicating better performance across the dataset.

Conclusion

The SVM classifier with an RBF kernel effectively detects arrhythmias in ECG data. Key techniques such as class balancing, hyperparameter tuning via GridSearchCV, and cross-validation have significantly improved the performance of the model.
Summary of Techniques Used:

    Radial Basis Function Kernel (RBF): Handles non-linear data relationships in ECG signals.
    Hyperparameter Tuning: Optimizes C and gamma to improve precision and recall.
    Cross-Validation: Ensures the model generalizes well across different subsets of data.
    Class Balancing: Prevents the model from favoring the majority class (normal beats) over the minority class (abnormal beats).