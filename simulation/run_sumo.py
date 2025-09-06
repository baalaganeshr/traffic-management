import os
import sys
import time
import pandas as pd
from pathlib import Path

# Setup import path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.sumo_connector import start_sumo, run_step, close_sumo
import traci

CONFIG_PATH = "sumo_network/simple.sumocfg"
SIMULATION_STEPS = 1000
SAVE_PATH = "simulation/simulated_data.csv"

def main():
    print("🚦 Starting SUMO simulation...")
    start_sumo(CONFIG_PATH, gui=False)

    data_log = []

    for _ in range(SIMULATION_STEPS):
        run_step()

        for vid in traci.vehicle.getIDList():
            data_log.append({
                "step": traci.simulation.getTime(),
                "vehicle_id": vid,
                "speed": traci.vehicle.getSpeed(vid),
                "x": traci.vehicle.getPosition(vid)[0],
                "y": traci.vehicle.getPosition(vid)[1]
            })

        time.sleep(0.01)  # Optional: simulate real time

    close_sumo()

    if data_log:
        df = pd.DataFrame(data_log)
        os.makedirs("simulation", exist_ok=True)
        df.to_csv(SAVE_PATH, index=False)
        print(f" Saved data to {SAVE_PATH}")
    else:
        print(" No vehicle data recorded.")

if __name__ == "__main__":
    main()
