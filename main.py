import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv('Rainfall.csv')

# Convert categorical target variable to numerical
df['rainfall'] = df['rainfall'].map({'yes': 1, 'no': 0})

# Fill missing values only for numerical columns
df.fillna(df.select_dtypes(include=[np.number]).mean(), inplace=True)

# Drop unnecessary columns
df.drop(['day', 'maxtemp', 'mintemp'], axis=1, inplace=True)

# Rename columns
df.rename(columns={
    'pressure ': 'pressure',
    'temparature': 'temperature',
    'humidity ': 'humidity',
    'cloud ': 'cloud'
}, inplace=True)

# Define features and target
X = df.drop(['rainfall'], axis=1)
y = df['rainfall']

# Save feature columns order
with open('feature_columns.pkl', 'wb') as f:
    pickle.dump(list(X.columns), f)

# Split data
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=2)

# Balance the dataset
ros = RandomOverSampler(sampling_strategy='minority', random_state=22)
X_train, y_train = ros.fit_resample(X_train, y_train)

# Scale features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)

# Train a model
model = SVC(kernel='rbf', probability=True)  # You can replace with LogisticRegression() or XGBClassifier()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_val)
accuracy = accuracy_score(y_val, y_pred)
print(f'Model Accuracy: {accuracy * 100:.2f}%')

# Save model and scaler
with open('model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('scaler.pkl', 'wb') as scaler_file:
    pickle.dump(scaler, scaler_file)

print("Model and scaler saved successfully!")