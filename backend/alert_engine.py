# backend/alert_engine.py

def generate_alert(row, status):
    """
    Generate alert if congestion is heavy.

    Args:
        row (dict): Row from traffic data
        status (str): Predicted congestion status

    Returns:
        dict or None: Alert info
    """
    if status == "Heavy":
        return {
            "timestamp": row['DateTime'],
            "junction": row['Junction'],
            "vehicle_count": row['Vehicles'],
            "status": status,
            "message": f" Heavy traffic at Junction {row['Junction']}"
        }
    return None
