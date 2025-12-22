FROM python:3.11-slim

WORKDIR /app

# Copy source code (will be overridden by volume mounts)
COPY commonpackages /opt/commonpackages
RUN pip install /opt/commonpackages

# Copy and nstall test dependencies
COPY tests/unit/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ../gateway /app/gateway
COPY ../website /app/website
COPY ../tests /app/tests

# Set Python path
ENV PYTHONPATH=/app/gateway/app:/app/website/app:/opt/commonpackages/src

# Default command
#CMD ["pytest", "tests/unit", "-v"]
