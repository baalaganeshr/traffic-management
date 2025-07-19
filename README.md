

##  UrbanFlow360 as a service: Design and Simulation of a Cloud-Based Platform for Real-Time Traffic Analytics.

UrbanFlow360 is a **cloud-based platform** that enables **real-time traffic simulation**, **ML-based congestion prediction**, and **smart alerting** for Indian cities like **Delhi** and **Bangalore**.

###  Features

* 🚦 **Traffic Simulation** using SUMO and synthetic data
*  **ML-Based Congestion Prediction** from CSV
*  **City Selection** (Delhi, Bangalore)
*  **Live Charts** (Speed trends, congestion heatmaps)
*  **Real-Time Alerts** (Heavy congestion hotspots)
*  **Event Injection** (simulate artificial disruptions)
*  **Streamlit Dashboard** for interactive control

---

## 🏁 Project Structure

```
urbanflow360/
├── analysis/               ← ML model + helpers
├── backend/                ← Traffic simulation logic
├── config/                 ← Config files for cities
├── data/                   ← Raw & cleaned data (Delhi, Bangalore)
├── data_utils/             ← Cleaning functions (e.g., delhi_cleaner.py)
├── frontend/               ← Streamlit UI (app.py)
├── logs/                   ← Alert logs, runtime logs
├── simulation/             ← SUMO simulation output / sample CSVs
├── sumo_network/           ← SUMO network files
├── test_stream.py          ← SUMO stream test runner
├── requirements.txt        ← Python dependencies
└── README.md               ← You are here
```

---

##  How to Run Locally

###  Step 1: Clone the repo

```bash
git clone https://github.com/KishanBouri/urbanflow360.git
cd urbanflow360
```

###  Step 2: Install requirements

```bash
pip install -r requirements.txt
```

### ▶ Step 3: Launch the Streamlit App

```bash
python -m streamlit run frontend/app.py
```

> **Note:** Don't use `streamlit run ...` directly if it shows error. Always use `python -m streamlit` to avoid environment conflicts.

---

##  ML Prediction Logic

* Model: RandomForestClassifier
* Trained on: Speed, weekday, and time-based features
* Input: Raw or cleaned traffic data (from Delhi or simulated)
* Output: `0 = Smooth`, `1 = Heavy`

---

##  SUMO Traffic Simulation

Simulate real-time vehicle flow using SUMO (Simulation of Urban MObility):

```bash
python test_stream.py
```

This generates a real-time stream and pushes it into the prediction pipeline.

---

##  Live Features Demo

*  Real-Time alert generation (`alert_generator.py`)
*  Speed prediction visualization
*  Separate processing logic for **Delhi** and **Bangalore**
*  Event-based simulation triggers

---

##  Tech Stack

* Python
* Streamlit
* Pandas, scikit-learn
* SUMO (for simulation)
* Matplotlib / Plotly
* Git / GitHub

---



## Teams Member

**Kishan Kumar Bouri**
**Akash Tiwari**
**Aashish Dewangan**
**Yash Mathur**

📌 GitHub: [@KishanBouri](https://github.com/KishanBouri)

---

##  Next Up (Planned)

*  Export map screenshots
*  Add multi-city support (e.g., Mumbai, Hyderabad)
* ☁️ Deploy to Streamlit Cloud or AWS EC2
*  Dashboard enhancements: congestion heatmaps, vehicle count animations

---
