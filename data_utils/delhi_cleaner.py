import pandas as pd

def convert_weekday_speed_to_xy_format(filepath: str) -> pd.DataFrame:
    # Load raw CSV
    df = pd.read_csv(filepath)

    # Melt from wide to long: One row per weekday + time
    df_long = df.melt(id_vars=['Time'], 
                      value_vars=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                      var_name="weekday", 
                      value_name="speed")

    # Clean speed column: remove ' km/h' and convert to float
    df_long['speed'] = df_long['speed'].astype(str).str.replace(' km/h', '', regex=False)
    df_long['speed'] = pd.to_numeric(df_long['speed'], errors='coerce')

    # Drop missing speeds
    df_long = df_long.dropna(subset=['speed'])

    # Simulate coordinates (you can improve this later with actual map logic)
    df_long['x'] = df_long.groupby('weekday').cumcount() * 10 + 50  # Vary X
    df_long['y'] = df_long['Time'].apply(lambda t: int(t.split(':')[0])) * 5 + 40  # Vary Y

    # Simulate other required columns
    df_long['step'] = df_long.groupby('weekday').cumcount()
    df_long['vehicle_id'] = 'veh_' + df_long.index.astype(str)
    df_long['Status'] = 'Smooth'  # Placeholder; will be overwritten by model

    return df_long
