import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

# Create dummy data
def generate_dummy_data():
    data = {
        'Speed': [20, 45, 10, 60, 50, 15, 25, 70, 35, 30],
        'Hour': [8, 9, 18, 20, 14, 7, 17, 10, 6, 12],
        'Weekday': [0, 1, 2, 3, 4, 5, 6, 1, 0, 3],
        'Congestion': ["Heavy", "Smooth", "Heavy", "Smooth", "Smooth",
                       "Heavy", "Heavy", "Smooth", "Heavy", "Smooth"]
    }
    return pd.DataFrame(data)

# Train and save model
def train_and_save_model(city):
    print(f"Training model for {city}...")

    df = generate_dummy_data()
    X = df[['Speed', 'Hour', 'Weekday']]
    y = df['Congestion']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save model
    model_path = os.path.join("analysis", f"{city.lower()}_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    for city in ["Delhi", "Bangalore"]:
        train_and_save_model(city)
