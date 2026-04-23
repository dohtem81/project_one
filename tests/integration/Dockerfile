FROM python:3.11-slim

WORKDIR /app

# Shared package
COPY packages/commonpackages /opt/commonpackages
RUN pip install /opt/commonpackages

# Service requirements
COPY tests/integration/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# Service code
COPY tests/integration/ ./

CMD ["python", "simulate_sensors.py"]