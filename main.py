import numpy as np
import pandas as pd
import pickle

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

# ------------------ Load & Preprocess Dataset ------------------

df = pd.read_csv('Rainfall.csv')

# Convert target variable to binary
df['rainfall'] = df['rainfall'].map({'yes': 1, 'no': 0})

# Clean up column names
df.columns = [col.strip().lower() for col in df.columns]
df.rename(columns={'temparature': 'temperature', 'humidity ': 'humidity', 'cloud ': 'cloud'}, inplace=True)

# Drop irrelevant columns if present
df.drop(columns=[col for col in ['day', 'maxtemp', 'mintemp'] if col in df.columns], inplace=True)

# Fill missing values in numeric columns
df.fillna(df.select_dtypes(include=np.number).mean(), inplace=True)

# ------------------ Define Features & Target ------------------

X = df.drop(columns=['rainfall'])
y = df['rainfall']

# Save feature columns order
with open('feature_columns.pkl', 'wb') as f:
    pickle.dump(X.columns.tolist(), f)

# ------------------ Train/Test Split ------------------

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# ------------------ Balance Using SMOTE ------------------

smote = SMOTE(random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# ------------------ Scale the Data ------------------

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)

# ------------------ Model & Hyperparameter Tuning ------------------

params = {
    'n_estimators': [100, 150],
    'max_depth': [3, 5],
    'learning_rate': [0.05, 0.1],
    'subsample': [0.8, 1.0]
}

grid = GridSearchCV(
    XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42),
    param_grid=params,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)

grid.fit(X_train, y_train)
model = grid.best_estimator_

# ------------------ Evaluate the Model ------------------

y_pred = model.predict(X_val)
accuracy = accuracy_score(y_val, y_pred)
print(f"Validation Accuracy: {accuracy * 100:.2f}%")
print("Best Hyperparameters:", grid.best_params_)

# Cross-validation (optional)
cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"Cross-Validated Accuracy: {cv_scores.mean() * 100:.2f}%")

# ------------------ Save Model and Scaler ------------------

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("✅ Model and Scaler saved successfully!")
