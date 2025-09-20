# Adaptive Signal Demo

This lightweight prototype demonstrates how VIN Traffic System can adjust signal timing dynamically.

## Run locally

```bash
streamlit run run_adaptive_demo.py
```

Adjust the sliders to model different demand patterns. The app synthesises counts from a virtual 360-degree sensor, allocates a two-phase signal plan, and visualises the recommended split along with an estimated delay reduction. The existing professional dashboard is untouched; use this demo as a sandbox for future CV or reinforcement learning controllers.
