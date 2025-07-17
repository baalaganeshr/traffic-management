# test_stream.py

from backend.simulate_data import simulate_traffic_stream
from backend.predictor import predict_congestion
from backend.alert_engine import generate_alert
import csv
import os

# Define paths
file_path = "data/traffic.csv"
log_file = "logs/events_log.csv"

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Create the log file if it doesn't exist (with UTF-8 encoding)
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'junction', 'vehicle_count', 'status', 'message'])

# Start simulation and processing
for row in simulate_traffic_stream(file_path, sleep_time=1):
    status = predict_congestion(row)
    print(f"[{row['DateTime']}] | Junction: {row['Junction']} | Vehicles: {row['Vehicles']} | Status: {status}")

    alert = generate_alert(row, status)
    if alert:
        print(f" {alert['message']} at {alert['timestamp']}")

        # Write alert to log file with UTF-8 encoding
        with open(log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                alert['timestamp'],
                alert['junction'],
                alert['vehicle_count'],
                alert['status'],
                alert['message']
            ])
