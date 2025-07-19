import traci

def start_sumo(config_path, gui=False):
    import sumolib  # optional
    from sumolib import checkBinary
    sumo_binary = "sumo-gui" if gui else "sumo"
    traci.start([sumo_binary, "-c", config_path])
    print("✅ SUMO started...")

def run_step():
    traci.simulationStep()
    vehicles = traci.vehicle.getIDList()
    for v_id in vehicles:
        speed = traci.vehicle.getSpeed(v_id)
        pos = traci.vehicle.getPosition(v_id)
        print(f"🚗 Vehicle {v_id} | Speed: {speed:.2f} | Position: {pos}")

def close_sumo():
    traci.close()
    print("🛑 SUMO simulation ended.")
