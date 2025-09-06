import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Load simulation data
df = pd.read_csv("simulation/simulated_data.csv")

# Create congestion label
df['congestion'] = (df['speed'] < 5).astype(int)

# Select features and target
X = df[['x', 'y', 'speed']]  # features
y = df['congestion']         # target

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("\n Classification Report:")
print(classification_report(y_test, y_pred))

print(" Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save the model
joblib.dump(model, "analysis/congestion_model.pkl")
print("\n Model saved to: analysis/congestion_model.pkl")
