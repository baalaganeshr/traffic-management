import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the simulated data
df = pd.read_csv("simulation/simulated_data.csv")

# Quick overview
print(" Dataset Shape:", df.shape)
print("\n Columns:", df.columns)
print("\n Sample Data:")
print(df.head())

# Convert time (if needed)
if 'time' in df.columns:
    df['time'] = pd.to_numeric(df['time'], errors='coerce')

# Basic stats
print("\n Speed Statistics:")
print(df['speed'].describe())

# Check missing values
print("\n🕳️ Missing Values:")
print(df.isnull().sum())

# Histogram of speeds
plt.figure(figsize=(8, 4))
sns.histplot(df['speed'], bins=20, kde=True)
plt.title("Speed Distribution of Vehicles")
plt.xlabel("Speed")
plt.ylabel("Count")
plt.grid(True)
plt.tight_layout()
plt.show()

# Vehicles with very low speed
low_speed = df[df['speed'] < 5]
print(f"\n Vehicles with Speed < 5: {len(low_speed)} ({(len(low_speed)/len(df))*100:.2f}%)")
