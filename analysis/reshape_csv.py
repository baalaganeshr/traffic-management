import pandas as pd

def reshape_heatmap_csv(file_path: str, metric: str) -> pd.DataFrame:
    """
    Convert a weekly time-heatmap CSV into long-format DataFrame for ML prediction.
    
    Args:
        file_path: Path to input CSV file
        metric: Name of the measurement (e.g., 'Speed', 'Congestion')

    Returns:
        DataFrame with columns: [Weekday, Hour, metric]
    """
    df = pd.read_csv(file_path)
    df_melted = df.melt(id_vars=["Time"], var_name="Weekday", value_name=metric)

    # Convert time string (e.g., "06:00") to hour integer
    df_melted["Hour"] = pd.to_datetime(df_melted["Time"], format="%H:%M", errors="coerce").dt.hour.fillna(0).astype(int)

    # Map weekdays to numbers
    weekday_map = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2,
        "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
    }
    df_melted["Weekday"] = df_melted["Weekday"].map(weekday_map)

    # Rename column to match ML model
    if metric.lower() == "speed":
        df_melted.rename(columns={metric: "Speed"}, inplace=True)
    else:
        # Fake Speed if using congestion or time: convert to inverse or scale
        df_melted[metric] = pd.to_numeric(df_melted[metric], errors='coerce').fillna(0)
        df_melted["Speed"] = 100 - df_melted[metric]
  # Simplified logic

    return df_melted[["Speed", "Hour", "Weekday"]]
