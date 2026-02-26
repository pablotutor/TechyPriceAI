# 🏢 TechyPrice AI: Dynamic Pricing & Bargain Hunter Engine

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Docker Compose](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

## 💼 Business Problem
In the short-term rental market (e.g., Airbnb, Booking), pricing asymmetry affects both sides of the marketplace:
1. **For Hosts:** Setting a price too high results in empty calendars, while setting it too low leaves money on the table. They lack real-time, data-driven pricing tools.
2. **For Guests & Investors:** Tourists and real estate investors struggle to identify true bargains in a saturated market, often not knowing if a listing is heavily overpriced or a hidden gem ripe for investment.

## 🎯 The Solution
**TechyPrice AI** is a Two-Sided Machine Learning system designed to bring transparency to the real estate market. 

* **🧠 Core Engine (Stacking Ensemble):** Calculates the "Fair Market Price" (Optimal nightly rate) for any property using a **Stacking Machine Learning architecture**. Instead of relying on a single algorithm, our system trains multiple base models (like Random Forest, LightGBM, and XGBoost) and uses a "Meta-Learner" (Linear Regression) to intelligently weigh their predictions, resulting in highly accurate and robust valuations.



* **🏠 Host Mode (Price Simulator):** An interactive interface for landlords to play with property parameters (bedrooms, amenities, location) and see how renovations impact their potential revenue.
* **🕵️ Investor Mode (Bargain Hunter):** A filtering engine that scans current listings, compares the *Actual Price* vs. the AI's *Predicted Price*, and highlights properties with the highest "Opportunity Score" (Residual Value).

## 🏗️ Architecture & Tech Stack
Unlike monolithic applications, this project follows a **Decoupled Microservices Architecture**, separating the Machine Learning inference engine from the user interface.

* **Data Processing:** Pandas, GeoPandas & Scikit-Learn.
* **Model:** Supervised Regression (Stacking Ensemble).
* **Backend/API (The Brain):** FastAPI (A lightweight, lightning-fast REST API to serve the ML model).
* **Frontend (The Face):** Streamlit (Interactive Dashboard for the end-user with Geospatial Heatmaps).
* **Containerization:** Docker & Docker Compose (Orchestrating multiple containers seamlessly).

## 📊 Project Structure

```text
techyprice-ai/
├── data/                  # Raw and processed datasets (Git ignored)
├── notebooks/             # EDA, Feature Engineering & Modeling (Jupyter)
├── backend/               # FastAPI Microservice
│   ├── models/            # Serialized trained models (.joblib)
│   ├── main.py            # API routing and model inference logic
│   ├── requirements.txt   # Backend dependencies
│   └── Dockerfile         # Backend container config
├── frontend/              # Streamlit Application
│   ├── assets/            # UI Images, logos, and styling assets
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

## 🔮 Roadmap & Future Improvements (v2.0 & Beyond)

We are actively scaling TechyPrice AI from a data science project into a full-fledged SaaS product.

### 1. Advanced AI & Agentic Workflows 🤖

* **Computer Vision "AI Appraisers":** Implement a multi-agent system where a specialized Computer Vision agent analyzes listing photos to score interior design quality and view aesthetics (e.g., "Does a view of the Royal Palace justify a 15% premium?").
* **National Expansion & Meta-Routing:** Train a generalized baseline model for the entire country (Spain) alongside highly specialized models for major cities. A routing agent will automatically direct API requests to the most accurate model based on coordinates.

### 2. Platform Scalability & Monetization 💳

* **Next.js Migration:** Rebuild the Streamlit frontend using Next.js/React to create a highly scalable, SEO-friendly web application with user authentication (Stripe integration for SaaS monetization).
* **PostgreSQL Database Migration:** Move away from static CSV files to a robust relational database (PostgreSQL + PostGIS for spatial queries) to handle daily dynamic data streams efficiently.

### 3. UX Automation & Business Intelligence 📈

* **1-Click Host Auto-Fill:** Allow hosts to simply paste their existing Airbnb URL. A backend scraper will automatically fetch all property features, photos, and amenities to feed the simulator instantly.
* **Competitor Price Tracking:** Alert hosts if similar nearby listings drop their prices.
* **Investor ROI Calculator:** Integrate real-time mortgage interest rates and estimated renovation costs into the Bargain Hunter to provide exact payback periods (Cap Rate & ROI) for real estate investors.

---

*Built with ❤️ by Pablo.*