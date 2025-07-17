
import pandas as pd
import time

def simulate_traffic_stream(file_path, sleep_time=1):

    """
    Simulates real-time traffic streaming from your dataset.

    Args:
        sleep_time (int): Seconds to wait between rows.

    Yields:
        dict: One row of traffic data as a dictionary.
    """

    # Your full file path to traffic.csv
    file_path = r"C:\Users\Hp\urbanflow360\data\traffic.csv"

    # Read and parse the timestamp
    df = pd.read_csv(file_path, parse_dates=['DateTime'])

    # Optional: sort chronologically
    df = df.sort_values('DateTime')

    for _, row in df.iterrows():
        yield row.to_dict()
        time.sleep(sleep_time)

