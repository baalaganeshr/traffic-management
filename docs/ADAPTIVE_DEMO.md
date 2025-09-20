# Adaptive Signal Demo

This lightweight prototype demonstrates how VIN Traffic System can adjust signal timing dynamically.

## Run locally

```bash
streamlit run run_adaptive_demo.py
```

### Features
- Scenario presets for morning peak, balanced evening, and eastbound incident conditions.
- Toggle between synthetic generation and recorded sample counts.
- Heuristic controller that reallocates north/south vs. east/west green splits and estimates delay reduction.
- Interactive charts, downloadable plan CSV, and responsive layout matching the VIN dashboard aesthetic.

Use this demo as a sandbox before plugging in real computer-vision counting or reinforcement learning policies.
