FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY data/ ./data/

# Create output directories
RUN mkdir -p /app/outputs /app/tasks

# Set Python path
ENV PYTHONPATH=/app

# Default command: run full pipeline
CMD ["python", "scripts/run_pipeline.py", "--pipeline", "all"]
