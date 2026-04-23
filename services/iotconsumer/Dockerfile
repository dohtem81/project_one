FROM python:3.11-slim

WORKDIR /app

# Shared package
COPY packages/commonpackages /opt/commonpackages
RUN pip install /opt/commonpackages

# Service requirements
<<<<<<< HEAD:iotconsumer/Dockerfile
COPY iotconsumer/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt
=======
COPY services/iotconsumer/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt
>>>>>>> 1ee62af (Add documentation and refactor project structure for IoT pipeline):services/iotconsumer/Dockerfile

# Service code
COPY services/iotconsumer/ ./

CMD ["python", "consumer.py"]