import sys
from pathlib import Path
from typing import Optional

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.adaptive_signal.sensor_stub import (
    SensorConfig,
    generate_sensor_data,
    list_scenarios,
    load_recorded_counts,
    scenario_config,
    scenario_description,
)
from backend.adaptive_signal.controller import ControllerConfig, evaluate_sequence

PRIMARY_COLOR = "#3b82f6"
SECONDARY_COLOR = "#0ea5e9"


def _inject_styles():
    st.markdown(
        """
        <style>
        .demo-hero {
            background: linear-gradient(120deg, rgba(59,130,246,0.25), rgba(14,165,233,0.18));
            border: 1px solid rgba(148,163,184,0.25);
            border-radius: 16px;
            padding: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .demo-hero h1 {
            margin: 0;
            font-size: 2rem;
        }
        .demo-meta {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
            color: rgba(226,232,240,0.9);
        }
        .demo-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.45rem 1rem;
            border-radius: 999px;
            border: 1px solid rgba(191,219,254,0.45);
            color: #eef2ff;
            text-decoration: none;
            background: rgba(15,23,42,0.3);
            box-shadow: 0 14px 28px rgba(15,23,42,0.32);
            letter-spacing: 0.01em;
        }
        .demo-pill:hover {
            background: rgba(59,130,246,0.3);
        }
        .metric-card {
            background: rgba(15,23,42,0.45);
            border: 1px solid rgba(148,163,184,0.2);
            border-radius: 12px;
            padding: 1rem 1.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_header():
    _inject_styles()
    col_left, col_right = st.columns([0.7, 0.3])
    with col_left:
        st.markdown(
            """
            <div class='demo-hero'>
              <div>
                <p class='demo-eyebrow'>VIN Concept Prototype</p>
                <h1>Adaptive signal timing demo</h1>
                <p>Experiment with synthetic 360-degree sensor feeds to see how VIN can reduce delay by reallocating
                green time between north/south and east/west phases.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_right:
        st.markdown(
            """
            <div style="display:flex; justify-content:flex-end; align-items:center; height:100%;">
              <a class='demo-pill' href='/'>\u2190 Back to site</a>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _scenario_controls():
    st.subheader("Scenario setup")
    scenarios = list(list_scenarios())
    scenario = st.selectbox("Traffic scenario", scenarios, index=0)
    st.caption(scenario_description(scenario))

    with st.expander("Fine tune (optional)", expanded=False):
        cfg = scenario_config(scenario)
        ns_flow = st.slider("North/South base volume", 4, 40, int(cfg.base_flow.get("North", 12)))
        ew_flow = st.slider("East/West base volume", 4, 40, int(cfg.base_flow.get("East", 12)))
        variability = st.slider("Demand variability", 0.05, 0.8, float(cfg.variability))
        seed = st.number_input("Random seed", value=int(cfg.seed or 0), min_value=0, step=1)
        cycles = st.slider("Number of cycles", 4, 24, 12)
        cycle_length = st.slider("Cycle length (seconds)", 60, 120, 80)
    refined_config = SensorConfig(
        base_flow={"North": ns_flow, "South": ns_flow, "East": ew_flow, "West": ew_flow},
        variability=variability,
        seed=seed or None,
    )
    controller_cfg = ControllerConfig(cycle_length=float(cycle_length))
    mode = st.radio("Data source", ["Generate synthetic", "Replay recorded"], horizontal=True)
    return scenario, mode, refined_config, controller_cfg, cycles


def _generate_counts(mode: str, scenario: str, config: SensorConfig, cycles: int) -> pd.DataFrame:
    if mode == "Replay recorded":
        try:
            return load_recorded_counts(scenario)
        except FileNotFoundError:
            st.warning("Recorded data not available for this scenario; falling back to synthetic feed.")
    return generate_sensor_data(config, cycles=cycles)


def _analysis_section(plans_df, counts_df):
    st.subheader("Controller insight")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Average NS green", f"{plans_df['ns_green'].mean():.0f}s")
    col_b.metric("Average EW green", f"{plans_df['ew_green'].mean():.0f}s")
    reduction = plans_df["predicted_delay_reduction_pct"].mean()
    col_c.metric("Estimated delay reduction", f"{reduction:.1f}%")

    chart = go.Figure()
    chart.add_trace(go.Bar(x=plans_df["cycle"], y=plans_df["ns_green"], name="North/South", marker_color=PRIMARY_COLOR))
    chart.add_trace(go.Bar(x=plans_df["cycle"], y=plans_df["ew_green"], name="East/West", marker_color=SECONDARY_COLOR))
    chart.update_layout(barmode="group", xaxis_title="Cycle", yaxis_title="Green time (s)")
    st.plotly_chart(chart, use_container_width=True)

    with st.expander("Detailed table"):
        summary = plans_df.merge(
            counts_df.pivot(index="cycle", columns="approach", values="vehicles").reset_index(),
            on="cycle",
            how="left",
        )
        st.dataframe(summary.round(2), use_container_width=True)
        st.download_button(
            "Download plan CSV",
            data=summary.to_csv(index=False).encode("utf-8"),
            file_name="vin_adaptive_plan.csv",
            mime="text/csv",
        )


def main():
    st.set_page_config(page_title="VIN Adaptive Signal Demo", layout="wide")
    _render_header()

    scenario, mode, sensor_cfg, controller_cfg, cycles = _scenario_controls()
    run = st.button("Compute plan", type="primary")

    if "demo_counts" not in st.session_state:
        st.session_state.demo_counts = None
        st.session_state.demo_plan = None

    if run:
        counts_df = _generate_counts(mode, scenario, sensor_cfg, cycles)
        plans_df = evaluate_sequence(counts_df, config=controller_cfg)
        st.session_state.demo_counts = counts_df
        st.session_state.demo_plan = plans_df

    if st.session_state.demo_counts is not None and st.session_state.demo_plan is not None:
        _analysis_section(st.session_state.demo_plan, st.session_state.demo_counts)
    else:
        st.info("Select a scenario and click 'Compute plan' to preview the adaptive schedule.")
        st.caption("The prototype allocates green time using heuristics. Replace the controller with reinforcement learning without changing the demo front-end.")


if __name__ == "__main__":
    main()
