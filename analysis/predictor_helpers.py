import pandas as pd
import joblib
import os

# Load the model
model_path = os.path.join("analysis", "congestion_model.pkl")
model = joblib.load(model_path)

# Define the features used during training (correct order)
FEATURE_ORDER = ['speed', 'x', 'y']

def predict_congestion(df):
    df_copy = df.copy()

    # Ensure all required features are present
    for col in FEATURE_ORDER:
        if col not in df_copy.columns:
            raise ValueError(f"Missing required feature: {col}")

    # Extract features and convert to NumPy array (removes column name mismatch issue)
    X = df_copy[FEATURE_ORDER].to_numpy()

    # Predict
    df_copy['prediction'] = model.predict(X)

    # Add readable labels
    df_copy['Status'] = df_copy['prediction'].map({0: "Smooth", 1: "Heavy"})

    return df_copy
