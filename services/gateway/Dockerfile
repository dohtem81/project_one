FROM python:3.11-slim

WORKDIR /app

# Copy and install shared objects package first
COPY packages/commonpackages /opt/commonpackages
RUN pip install /opt/commonpackages

# Service requirements
<<<<<<< HEAD:gateway/Dockerfile
COPY gateway/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt
=======
COPY services/gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt
>>>>>>> 1ee62af (Add documentation and refactor project structure for IoT pipeline):services/gateway/Dockerfile

# Service code
COPY services/gateway/ ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
