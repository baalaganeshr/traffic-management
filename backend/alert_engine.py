def generate_alert(row, status=None, city="Delhi"):
    alert = None

    if city == "Delhi":
        if status == "Heavy":
            alert = {
                "Time": row.get("Time", ""),
                "Location": f"X:{row.get('x', 'NA')} / Y:{row.get('y', 'NA')}",
                "Severity": "High",
                "Message": "Heavy congestion detected."
            }

    elif city == "Bangalore":
        try:
            congestion = float(row.get("Congestion Level", 0))
            volume = float(row.get("Traffic Volume", 0))
        except:
            congestion = 0
            volume = 0

        if congestion > 70 or volume > 1000:  # You can tweak these values
            alert = {
                "Time": row.get("Date", ""),
                "Location": row.get("Area Name", "Unknown"),
                "Severity": "High" if congestion > 80 else "Medium",
                "Message": f"Congestion: {congestion}%, Volume: {volume}"
            }

    return alert
