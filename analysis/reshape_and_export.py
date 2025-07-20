from reshape_csv import reshape_heatmap_csv

# Adjust the path if file is not in the same folder
df = reshape_heatmap_csv("data/delhi/2024_week_day_congestion_city.csv", metric="Congestion")


# Save reshaped output
df.to_csv("data/reshaped_congestion.csv", index=False)

print("✅ Reshaped file saved to data/reshaped_congestion.csv")
