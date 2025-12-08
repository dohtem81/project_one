FROM python:3.11-slim

WORKDIR /app

# Copy and install shared objects package first
COPY commonpackages /opt/commonpackages
RUN pip install /opt/commonpackages

# Service requirements
COPY gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

# Service code
COPY gateway/ ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
