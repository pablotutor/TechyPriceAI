# 🏢 TechyPrice AI: Dynamic Pricing Engine

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Docker Compose](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

## 💼 Business Problem
In the short-term rental market (e.g., Airbnb, Booking), pricing is the most critical lever for profitability. Setting a price too high results in empty calendars and zero revenue. Setting it too low means leaving money on the table.

**The Challenge:** Property managers and individual landlords often rely on "gut feeling" or static seasonal pricing. They lack a real-time, data-driven tool to dynamically adjust prices based on property features, location, and market demand, similar to how airlines and large hotel chains operate.

## 🎯 The Solution
**TechyPrice AI** is a Full-Stack Machine Learning system designed to act as a Smart Pricing Oracle. It:
1.  **Predicts:** Calculates the "Fair Market Price" (Optimal nightly rate) for a specific property in Madrid using a Regression model.
2.  **Analyzes:** Identifies which features add the most value to a property (e.g., Number of bedrooms, Air Conditioning, Distance to the city center).
3.  **Simulates:** Provides an interactive interface for landlords to play with property parameters and see how renovations or feature upgrades impact their potential revenue.

## 🏗️ Architecture & Tech Stack
Unlike monolithic applications, this project follows a **Decoupled Microservices Architecture**, separating the Machine Learning inference engine from the user interface.



* **Data Processing:** Pandas, GeoPandas & Scikit-Learn Pipelines.
* **Model:** Supervised Regression (XGBoost / Random Forest Regressor).
* **Backend/API (The Brain):** FastAPI (A lightweight, lightning-fast REST API to serve the ML model).
* **Frontend (The Face):** Streamlit (Interactive Dashboard for the end-user).
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

Currently in early development. The following features are planned:

### 1. Advanced Feature Engineering

* **Geospatial Distance:** Calculate the exact Haversine distance from the property to the city center (Puerta del Sol) to improve price accuracy.
* **Amenity NLP:** Extract and process keyword tags from the property description (e.g., "Rooftop", "Jacuzzi") using NLP techniques.

### 2. Market Intelligence Dashboard

* **Bargain Hunter Mode:** Compare a user-inputted actual price against the AI's predicted price to classify the listing as an "Underpriced Bargain" or "Overpriced".
* **Heatmaps:** Integrate interactive maps (`folium` or `pydeck`) to visualize average predicted prices across different neighborhoods in Madrid.

### 3. Continuous Integration / MLOps

* **Automated Retraining:** Script a pipeline to download fresh data from InsideAirbnb monthly and retrain the model if performance degrades (Data Drift).
* **Cloud Deployment:** Deploy the Docker Compose cluster to AWS (EC2/ECS) or Google Cloud Run for public access.

---

*Built with ❤️ by Pablo.*