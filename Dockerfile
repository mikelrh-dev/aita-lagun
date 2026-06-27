# Aita-Lagun — Multi-Agent Assistant for Elderly Care
#
# Stage: Production image
# Base: python:3.10-slim (matches project requires-python, minimal footprint)
# Layers: 3 (dependencies → source → entrypoint) optimized for Docker caching

FROM python:3.10-slim

WORKDIR /app

# Layer 1: Install Python dependencies (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2: Copy application source code
COPY . .

# Environment: unbuffered stdout/stderr for Cloud Run log streaming
ENV PYTHONUNBUFFERED=1

# Entry point: ADK CLI agent mode (stdin/stdout interaction)
CMD ["python", "-m", "agents.agent"]
