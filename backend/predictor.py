# backend/predictor.py

def predict_congestion(row):
    """
    Simple rule-based predictor for traffic congestion.

    Args:
        row (dict): One row of traffic data.

    Returns:
        str: Congestion status - 'Smooth', 'Moderate', or 'Heavy'
    """
    vehicles = row.get('Vehicles', 0)  # Safe access to vehicle count

    if vehicles <= 10:
        return 'Smooth'
    elif vehicles <= 20:
        return 'Moderate'
    else:
        return 'Heavy'



