import pandas as pd

def simulate_traffic_stream(csv_path, sleep_time=0.2, event_config={}):
    df = pd.read_csv(csv_path)

    for i, row in df.iterrows():
        row = row.to_dict()

        # Convert 'Time' column to datetime.time if available
        if 'Time' in row:
            try:
                current_time = datetime.strptime(row['Time'], "%I:%M %p").time()
            except:
                current_time = None
        else:
            current_time = None

        # Inject Congestion if event matches
        if event_config and row.get('x') and row.get('y') and current_time:
            event_time = event_config["event_time"]
            duration = event_config["event_duration"]
            delta_minutes = abs(datetime.combine(datetime.today(), current_time) -
                                datetime.combine(datetime.today(), event_time)).total_seconds() / 60

            # Only inject within time + radius
            if delta_minutes <= duration:
                dx = abs(row['x'] - event_config["event_x"])
                dy = abs(row['y'] - event_config["event_y"])
                dist = (dx**2 + dy**2)**0.5

                if dist <= event_config["event_radius"]:
                    row['speed'] = max(5, row.get('speed', 30) * 0.3)  # Simulate congestion

        yield row
        if sleep_time:
            time.sleep(sleep_time)
