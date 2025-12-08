FROM python:3.11-slim

WORKDIR /app

# Shared package
COPY commonpackages /opt/commonpackages
RUN pip install /opt/commonpackages

# Service requirements
COPY iotconsumer/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

# Service code
COPY iotconsumer/ ./

CMD ["python", "consumer.py"]