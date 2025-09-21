````markdown
# 🚦 VIN Traffic Management System v2.0

**Production-grade traffic monitoring and analytics platform** with enterprise-level deployment capabilities, comprehensive health monitoring, and bulletproof configuration management.

## ✨ Highlights

- Professional dashboard: Monitor, Analytics, Map, Data tabs
- Live simulation: stream samples with auto‑refresh and status
- AI signals: congestion prediction and simple, readable alerts
- Analytics: clean histograms and trends (Plotly), CSV export
- Map: city overlays with severity coloring (pydeck)
- Dockerized: Nginx serves site, proxies dashboard at `/dashboard/`

---

## 📁 Structure (selected)

```
traffic-management/
├─ website/                 # Static site served by Nginx
│  ├─ index.html            # Home with “Open Dashboard”
│  ├─ styles.css            # Theme + layout
│  ├─ script.js             # Cursor glow and minor UX
│  └─ nginx.conf            # Proxies /dashboard/ to Streamlit
├─ frontend/                # Streamlit UI
│  └─ app_unified_improved.py
├─ backend/                 # Simulation + predictors + alerts
├─ analysis/                # Models and helpers
├─ data/                    # Datasets
├─ run_professional_improved.py
├─ docker-compose.yml       # Nginx + Streamlit services
└─ Dockerfile               # Streamlit image
```

---

## 🚀 Quick Start (Docker)

```bash
# From repo root
docker compose -f traffic-management/docker-compose.yml up -d --build

# Open
#   Site:       http://localhost/
#   Dashboard:  http://localhost/dashboard/
#   Streamlit:  http://localhost:8511/   # direct, useful for debugging

# Stop
docker compose -f traffic-management/docker-compose.yml down
```

---

## 🎯 Dashboard Summary

- Monitor: start/stop collection, KPIs, live sparkline, simple table
- Analytics: source (Live/Processed), metric (Speed/Volume), histogram + trend
- Map: severity‑colored scatter layers; tooltips
- Data: quick preview + CSV export

---

## 🤖 ML Signals (overview)

- Models: scikit‑learn‑based congestion estimator (see `analysis/`)
- Inputs: speed, time windows, and derived context
- Output: simple levels used by alert helpers and maps

---

## 🐳 Services

- `website` (Nginx)
  - Serves `website/` at `/`
  - Proxies `/dashboard/` to Streamlit with WebSocket upgrade
- `dashboard` (Streamlit)
  - Runs `run_professional_improved.py` with `--server.baseUrlPath=/dashboard`

---

## 🧩 Local Development (optional)

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r traffic-management/requirements.txt
STREAMLIT_SERVER_BASEURLPATH=/dashboard streamlit run traffic-management/run_professional_improved.py \
  --server.port=8501 --server.address=0.0.0.0 --server.headless=true
```

---

## 🧰 Troubleshooting

- Blank loading screen behind Nginx: ensured WebSocket upgrade on `/dashboard/_stcore/stream` (configured).
- Charts schema error (Altair intervals): replaced with Plotly histograms/trends.
- Browser cache: use Ctrl+F5 after updates.

---

## 🔗 Links

- Repo: https://github.com/baalaganeshr/traffic-management
- Issues: https://github.com/baalaganeshr/traffic-management/issues

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 Support

For support and questions:
1. Check the [Issues](https://github.com/baalaganeshr/traffic-management/issues) page
2. Review the documentation
3. Contact the development team

---

**🎯 Professional Traffic Management System - Powered by AI & Analytics**
