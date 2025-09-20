import sys
from pathlib import Path
from typing import Iterable

import pandas as pd
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


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .demo-hero {
            background: linear-gradient(135deg, 
                rgba(59,130,246,0.12) 0%, 
                rgba(14,165,233,0.08) 50%, 
                rgba(37,99,235,0.1) 100%);
            border: 2px solid rgba(59,130,246,0.25);
            border-radius: 24px;
            padding: 3rem 3rem;
            margin-bottom: 2.5rem;
            backdrop-filter: blur(15px);
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(59,130,246,0.1), 
                        inset 0 1px 0 rgba(255,255,255,0.1);
        }
        .demo-hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(59,130,246,0.4), 
                transparent);
        }
        .demo-hero h1 {
            margin: 0 0 1rem 0;
            font-size: 2.6rem;
            font-weight: 800;
            background: linear-gradient(135deg, 
                #2563eb 0%, 
                #3b82f6 25%, 
                #0ea5e9 50%, 
                #06b6d4 75%, 
                #0891b2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
            line-height: 1.1;
            text-align: center;
            position: relative;
        }
        .demo-hero h1::after {
            content: '';
            position: absolute;
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #3b82f6, #0ea5e9);
            border-radius: 2px;
        }
        .demo-hero p {
            font-size: 1.15rem;
            line-height: 1.7;
            opacity: 0.85;
            text-align: center;
            max-width: 600px;
            margin: 0 auto 1.5rem auto;
            font-weight: 400;
            color: #374151;
        }
        .demo-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.95rem;
            border: 2px solid rgba(59,130,246,0.4);
            color: #ffffff;
            text-decoration: none;
            background: linear-gradient(135deg, rgba(59,130,246,0.2) 0%, rgba(37,99,235,0.15) 100%);
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px rgba(59,130,246,0.15), inset 0 1px 0 rgba(255,255,255,0.1);
            letter-spacing: 0.02em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .demo-pill::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s ease;
        }
        .demo-pill:hover {
            background: linear-gradient(135deg, rgba(59,130,246,0.35) 0%, rgba(37,99,235,0.25) 100%);
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 16px 40px rgba(59,130,246,0.25), inset 0 1px 0 rgba(255,255,255,0.2);
            border-color: rgba(59,130,246,0.6);
            color: #f8fafc;
        }
        .demo-pill:hover::before {
            left: 100%;
        }
        .demo-pill:active {
            transform: translateY(-1px) scale(0.98);
        }
        .scenario-card {
            margin-top: 1.5rem;
            background: linear-gradient(135deg, 
                rgba(15,23,42,0.85) 0%, 
                rgba(30,41,59,0.75) 50%, 
                rgba(51,65,85,0.8) 100%);
            border: 2px solid rgba(59,130,246,0.3);
            border-radius: 20px;
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(59,130,246,0.15), 
                        inset 0 1px 0 rgba(59,130,246,0.1);
        }
        .scenario-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(59,130,246,0.6), 
                transparent);
            transition: left 0.6s ease;
        }
        .scenario-card:hover {
            border-color: rgba(59,130,246,0.5);
            transform: translateY(-4px) scale(1.01);
            box-shadow: 0 20px 60px rgba(59,130,246,0.25), 
                        inset 0 1px 0 rgba(59,130,246,0.2);
        }
        .scenario-card:hover::before {
            left: 100%;
        }
        .scenario-card h4 {
            margin: 0 0 1.2rem 0;
            font-size: 1.25rem;
            font-weight: 700;
            color: #f8fafc;
            letter-spacing: -0.01em;
            position: relative;
        }
        .scenario-inline {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            font-size: 0.95rem;
            color: #e2e8f0;
            line-height: 1.5;
        }
        .scenario-inline span {
            padding: 0.6rem 1.2rem;
            border-radius: 25px;
            background: linear-gradient(135deg, 
                rgba(59,130,246,0.25) 0%, 
                rgba(37,99,235,0.2) 100%);
            border: 1px solid rgba(59,130,246,0.4);
            color: #93c5fd;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        .scenario-inline span:hover {
            background: linear-gradient(135deg, 
                rgba(59,130,246,0.4) 0%, 
                rgba(37,99,235,0.3) 100%);
            border-color: rgba(59,130,246,0.6);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59,130,246,0.3);
            color: #dbeafe;
        }
        
        /* Mobile Responsiveness */
        @media (max-width: 768px) {
            .demo-hero {
                padding: 2rem 1.5rem;
                margin-bottom: 2rem;
                border-radius: 16px;
            }
            .demo-hero h1 {
                font-size: 2.2rem;
                line-height: 1.2;
            }
            .demo-hero h1::after {
                width: 50px;
                height: 2px;
            }
            .demo-hero p {
                font-size: 1.05rem;
                padding: 0 1rem;
            }
            .demo-pill {
                padding: 1rem 1.5rem;
                font-size: 0.95rem;
                min-height: 48px;
            }
            .scenario-card {
                padding: 1.5rem;
                margin-top: 1rem;
                border-radius: 16px;
            }
            .scenario-card h4 {
                font-size: 1.1rem;
                margin-bottom: 1rem;
            }
            .scenario-inline {
                gap: 0.6rem;
                font-size: 0.95rem;
            }
            .scenario-inline span {
                padding: 0.5rem 1rem;
                font-size: 0.9rem;
                min-height: 36px;
                display: flex;
                align-items: center;
            }
        }
        
        @media (max-width: 480px) {
            .demo-hero {
                padding: 1.5rem 1rem;
                margin-bottom: 1.5rem;
            }
            .demo-hero h1 {
                font-size: 1.8rem;
                line-height: 1.3;
            }
            .demo-hero h1::after {
                width: 40px;
            }
            .demo-hero p {
                font-size: 1rem;
                padding: 0;
            }
            .demo-pill {
                padding: 0.8rem 1.2rem;
                font-size: 0.9rem;
                width: 100%;
                text-align: center;
                justify-content: center;
            }
            .scenario-card {
                padding: 1.2rem;
                margin-top: 1rem;
            }
            .scenario-card h4 {
                font-size: 1rem;
                text-align: center;
            }
            .scenario-inline {
                justify-content: center;
                gap: 0.4rem;
            }
            .scenario-inline span {
                padding: 0.4rem 0.8rem;
                font-size: 0.85rem;
                text-align: center;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_header() -> None:
    _inject_styles()
    col_left, col_right = st.columns([0.75, 0.25])
    with col_left:
        st.markdown(
            """
            <div class='demo-hero'>
              <div>
                <p style="text-transform:uppercase; letter-spacing:0.2em; font-size:0.8rem; color:rgba(59,130,246,0.8); margin:0 0 .5rem 0; font-weight: 600;">🚦 Interactive Demo</p>
                <h1>Smart Traffic Signal Optimizer</h1>
                <p style="margin:0; color:rgba(226,232,240,0.95); max-width:600px; font-size:1.1rem;">Watch how AI optimizes traffic signals in real-time. Adjust traffic scenarios and see instant improvements in intersection flow and delay reduction.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_right:
        st.markdown(
            """
            <div style="display:flex; justify-content:flex-end; align-items:center; height:100%; gap: 1rem;">
              <a class='demo-pill' href='/' style='text-decoration: none;'>
                <span style='font-size: 1.1rem; font-weight: 700;'>←</span>
                <span style='font-weight: 600;'>Back to Home</span>
              </a>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _scenario_card(name: str, cfg: SensorConfig) -> None:
    base_summary = " ".join(
        f"<span>{approach}: {int(flow)}</span>" for approach, flow in cfg.base_flow.items()
    )
    st.markdown(
        f"""
        <div class='scenario-card'>
          <h4>{name}</h4>
          <p style='margin:0 0 .6rem 0;'>{scenario_description(name)}</p>
          <div class='scenario-inline'>{base_summary}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _scenario_controls():
    st.subheader("Scenario setup")
    left, right = st.columns([0.6, 0.4])
    with left:
        scenarios = list(list_scenarios())
        scenario = st.selectbox("Traffic scenario", scenarios, index=0)
        base_cfg = scenario_config(scenario)
        _scenario_card(scenario, base_cfg)
    with right:
        mode = st.radio("Data source", ["Generate synthetic", "Replay recorded"], horizontal=False)
        cycles = st.slider("Number of cycles", 4, 24, 12, help="Each cycle represents one full NS/EW rotation.")
        cycle_length = st.slider("Cycle length (seconds)", 60, 120, 80)

    with st.expander("Fine tune (optional)", expanded=False):
        ns_flow = st.slider("North/South base volume", 4, 40, int(base_cfg.base_flow.get("North", 12)))
        ew_flow = st.slider("East/West base volume", 4, 40, int(base_cfg.base_flow.get("East", 12)))
        variability = st.slider("Demand variability", 0.05, 0.8, float(base_cfg.variability))
        seed = st.number_input("Random seed", value=int(base_cfg.seed or 0), min_value=0, step=1)

    refined_config = SensorConfig(
        base_flow={"North": ns_flow, "South": ns_flow, "East": ew_flow, "West": ew_flow},
        variability=variability,
        seed=seed or None,
    )
    controller_cfg = ControllerConfig(cycle_length=float(cycle_length))
    return scenario, mode, refined_config, controller_cfg, cycles


def _generate_counts(mode: str, scenario: str, config: SensorConfig, cycles: int) -> pd.DataFrame:
    if mode == "Replay recorded":
        try:
            return load_recorded_counts(scenario)
        except FileNotFoundError:
            st.warning("Recorded data not available for this scenario; falling back to synthetic feed.")
    return generate_sensor_data(config, cycles=cycles)


def _analysis_section(plans_df: pd.DataFrame, counts_df: pd.DataFrame) -> None:
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

    queue_chart = go.Figure()
    for approach in counts_df["approach"].unique():
        df = counts_df[counts_df["approach"] == approach]
        queue_chart.add_trace(
            go.Scatter(x=df["cycle"], y=df["queue"], mode="lines+markers", name=f"{approach} queue")
        )
    queue_chart.update_layout(xaxis_title="Cycle", yaxis_title="Estimated queue (vehicles)", legend_title="Approach")
    st.plotly_chart(queue_chart, use_container_width=True)

    with st.expander("Detailed plan and counts"):
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


def main() -> None:
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
        st.info("Select a scenario, choose a data source, and click **Compute plan** to preview the adaptive schedule.")
        st.caption("The prototype uses heuristics today. Replace the controller with reinforcement learning without changing this front-end.")


if __name__ == "__main__":
    main()
