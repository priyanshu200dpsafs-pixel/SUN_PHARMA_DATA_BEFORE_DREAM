FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY webapp/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY webapp/backend /app/webapp/backend

# The backend depends on datasets and model outputs from the root project structure
COPY processed_data /app/processed_data
COPY outputs /app/outputs
COPY code /app/code

# Expose API port
EXPOSE 8000

# Start Uvicorn server
CMD ["uvicorn", "webapp.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
