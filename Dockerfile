# Stage 1: Build the React Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/webapp/frontend
COPY webapp/frontend/package*.json ./
RUN npm install
COPY webapp/frontend/ ./
RUN npm run build

# Stage 2: Build the Python FastAPI Backend & Combine
FROM python:3.13-slim

# Set working directory to project root
WORKDIR /app

# Install system dependencies (needed for geopandas/xgboost sometimes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY webapp/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY webapp/backend /app/webapp/backend

# Copy the data folders needed for the ML models
COPY processed_data /app/processed_data
COPY outputs /app/outputs
COPY raw_data /app/raw_data
COPY code /app/code

# Copy the built React app from Stage 1 into the backend's expected directory
COPY --from=frontend-builder /app/webapp/frontend/dist /app/webapp/frontend/dist

# Expose the Hugging Face required port
EXPOSE 7860

# Run the unified FastAPI server
CMD ["uvicorn", "webapp.backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
