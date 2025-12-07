FROM python:3.11-slim

WORKDIR /app

# Copy requirements.txt first (this file should exist in iotconsumer/)
# COPY iotconsumer/requirements.txt ./requirements.txt
# Copy the rest of the application
COPY iotconsumer/ ./

# Copy and install shared objects package first
COPY sharedobjects/ /opt/sharedobjects/
RUN pip install -e /opt/sharedobjects

RUN pip install --no-cache-dir -r ./requirements.txt


CMD ["python", "consumer.py"]
