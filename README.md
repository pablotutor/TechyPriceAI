# 🏢 TechyPrice AI: Dynamic Pricing & Bargain Hunter Engine

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Docker Compose](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

## 💼 Business Problem
In the short-term rental market (e.g., Airbnb, Booking), pricing asymmetry affects both sides of the marketplace:
1. **For Hosts:** Setting a price too high results in empty calendars, while setting it too low leaves money on the table. They lack real-time, data-driven pricing tools.
2. **For Guests:** Tourists and renters struggle to identify true bargains in a saturated market, often not knowing if a listing is heavily overpriced or a hidden gem.

## 🎯 The Solution
**TechyPrice AI** is a Two-Sided Machine Learning system designed to bring transparency to the real estate market. 

* **🧠 Core Engine:** Calculates the "Fair Market Price" (Optimal nightly rate) for any property in Madrid using an advanced XGBoost Regression model and Geospatial Analytics.
* **🏠 Host Mode (Price Simulator):** An interactive interface for landlords to play with property parameters (bedrooms, amenities, location) and see how renovations impact their potential revenue.
* **🕵️ Guest Mode (Bargain Hunter):** A filtering engine that scans current listings, compares the *Actual Price* vs. the AI's *Predicted Price*, and ranks properties by their "Opportunity Score" (finding the most underpriced gems).

## 🏗️ Architecture & Tech Stack
Unlike monolithic applications, this project follows a **Decoupled Microservices Architecture**, separating the Machine Learning inference engine from the user interface.

* **Data Processing:** Pandas, GeoPandas & Scikit-Learn Pipelines.
* **Model:** Supervised Regression (XGBoost / Random Forest Regressor).
* **Backend/API (The Brain):** FastAPI (A lightweight, lightning-fast REST API to serve the ML model).
* **Frontend (The Face):** Streamlit (Interactive Dashboard for the end-user with Geospatial Heatmaps).
* **Containerization:** Docker & Docker Compose (Orchestrating multiple containers seamlessly).

## 📊 Project Structure

```text
techyprice-ai/
├── data/                  # Raw and processed datasets (Git ignored)
├── notebooks/             # EDA, Feature Engineering & Modeling (Jupyter)
├── models/                # Serialized trained models (.joblib)
├── backend/               # FastAPI Microservice
│   ├── main.py            # API routing and model inference logic
│   ├── requirements.txt   # Backend dependencies
│   └── Dockerfile         # Backend container config
├── frontend/              # Streamlit Application
│   ├── app.py             # UI and API connection logic
│   ├── requirements.txt   # Frontend dependencies
│   └── Dockerfile         # Frontend container config
├── docker-compose.yml     # Multi-container orchestration
└── README.md              # Project documentation

```

## 🚀 How to Run (Docker Compose)

Because this project uses a decoupled architecture, we use `docker-compose` to spin up both the Backend API and the Frontend Dashboard simultaneously.

1. **Build and run the cluster:**

```bash
docker-compose up --build

```

2. **Access the applications:**

* **Frontend Dashboard:** Open your browser at `http://localhost:8501`
* **Backend API Docs (Swagger UI):** Open your browser at `http://localhost:8000/docs`

## 🔮 Roadmap & Future Improvements

Currently in early development. The following features are planned for v2.0:

### 1. Advanced Feature Engineering

* **Amenity NLP:** Extract and process keyword tags from the property description (e.g., "Rooftop", "Jacuzzi") using NLP techniques to measure emotional premium.
* **Time-Series Seasonality:** Integrate Prophet to adjust the baseline "Fair Price" based on the month of the year or local events (e.g., Champions League final in Madrid).

### 2. Market Intelligence Dashboard

* **Dynamic Hexagon Heatmaps:** Upgrade the standard map to an interactive `pydeck` H3 hexagon map to visualize average opportunity scores across different micro-neighborhoods.

### 3. Continuous Integration / MLOps

* **Automated Retraining:** Script a pipeline to download fresh data from InsideAirbnb monthly and retrain the model if performance degrades (Data Drift).
* **Cloud Deployment:** Deploy the Docker Compose cluster to AWS (EC2/ECS) or Google Cloud Run for public access.

---

*Built with ❤️ by Pablo.*