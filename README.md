# Sun Pharma Market Attractiveness Dashboard

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![React](https://img.shields.io/badge/React-18-blue)

A high-performance geospatial analytics dashboard built to optimize market entry strategies for Sun Pharma. This system utilizes a custom Market Attractiveness Index (MAI) driven by a Gaussian Mixture Model to identify high-viability expansion targets across India.

## 🚀 Architecture

This repository is split into two primary components:
1. **FastAPI Backend (`webapp/backend/`)**: Serves complex geospatial computations, machine learning predictions (XGBoost), and Shapley values to explain model insights.
2. **React/Vite Frontend (`webapp/frontend/`)**: An interactive, high-speed dashboard featuring interactive maps, dynamic clustering, and scenario modeling.

*Note: Large processed datasets (`processed_data/`) and machine learning models (`outputs/`) are strictly `.gitignore`'d for security and repository health. Ensure you have these directories present locally before building.*

## 🐳 Running with Docker

The absolute easiest way to deploy this application is using the provided Docker Compose configuration.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed and running.
- Ensure your `processed_data/` and `outputs/` folders are present in the root directory.

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/priyanshu200dpsafs-pixel/SUN_PHARMA_DATA_BEFORE_DREAM.git
   cd SUN_PHARMA_DATA_BEFORE_DREAM
   ```

2. Build and launch the containers:
   ```bash
   docker-compose up -d --build
   ```

3. Access the application:
   - **Frontend Dashboard**: [http://localhost](http://localhost)
   - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🛠️ Manual Development Setup

If you prefer to run the servers independently for development without Docker:

### Backend
```bash
cd webapp/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd webapp/frontend
npm install
npm run dev
```

## 🔒 Security Note
This repository contains data protection rules via `.gitignore` to prevent any sensitive pipeline artifacts from being committed. Do not bypass these rules.
