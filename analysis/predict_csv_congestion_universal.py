import pandas as pd
import joblib
import os
import re

def predict_csv_congestion(df: pd.DataFrame, city: str) -> pd.DataFrame:
    """
    Universal prediction function for varied traffic CSVs.
    """

    df = df.copy()

    # -------------------------------
    # Step 1: Try to identify 'Speed'
    # -------------------------------
    speed_col = None
    for col in df.columns:
        if col.lower() in ['speed', 'avg speed', 'average speed', 'vehicles', 'congestion']:
            speed_col = col
            break

    if speed_col is None:
        raise ValueError("No usable speed or vehicle column found.")

    # Clean numeric value from text like "22 km/h"
    df['Speed'] = pd.to_numeric(df[speed_col].astype(str).str.extract(r'([\d.]+)')[0], errors='coerce')

    # Optional: Invert congestion or vehicle counts to simulate speed
    if speed_col.lower() in ['vehicles', 'congestion']:
        df['Speed'] = 100 - df['Speed']

    df['Speed'] = df['Speed'].fillna(30)

    # -------------------------------
    # Step 2: Extract Hour
    # -------------------------------
    df['Hour'] = 0
    time_col = None
    for col in df.columns:
        if 'time' in col.lower():
            time_col = col
            break

    if time_col:
        try:
            df['Hour'] = pd.to_datetime(df[time_col], errors='coerce').dt.hour.fillna(0).astype(int)
        except Exception:
            df['Hour'] = 0

    # -------------------------------
    # Step 3: Extract Weekday
    # -------------------------------
    df['Weekday'] = 0
    date_col = None
    for col in df.columns:
        if 'date' in col.lower():
            date_col = col
            break

    if date_col:
        try:
            df['Weekday'] = pd.to_datetime(df[date_col], errors='coerce').dt.dayofweek.fillna(0).astype(int)
        except Exception:
            df['Weekday'] = 0

    # -------------------------------
    # Step 4: Predict
    # -------------------------------
    features = df[['Speed', 'Hour', 'Weekday']].fillna(0)

    model_path = os.path.join("analysis", f"{city.lower()}_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = joblib.load(model_path)

    df['Congestion'] = model.predict(features)

    return df
